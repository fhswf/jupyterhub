from urllib.parse import urlsplit

from tornado import gen
from tornado.escape import url_escape
from tornado.httputil import url_concat

from traitlets import (
    Unicode, Integer, Dict, TraitError, List, Bool, Any,
    Type, Set, Instance, Bytes, Float,
    observe, default,
)

from jupyterhub.auth import Authenticator
from jupyterhub.handlers.login import LoginHandler, LogoutHandler

from oauthenticator.google import GoogleOAuthenticator, GoogleLoginHandler, GoogleOAuthHandler
from oauthenticator.github import GitHubOAuthenticator, GitHubLoginHandler
from jhub_cas_authenticator.cas_auth import CASAuthenticator, CASLoginHandler
import pdb


class MultiLoginHandler(LoginHandler):

    def _render(self, login_error=None):
        """
        Mainly changes the template, also simplify a bit
        """
        context = {
            'google': {
                'enabled': self.authenticator.enable_google,
            },
            'github': {
                'enabled': self.authenticator.enable_github,
            },
            'nih': {
                'enabled': self.authenticator.enable_nih,
            },
        }
        nextval = self.get_argument('next', default='')
        return self.render_template('nlm/login.html',
            next=url_escape(nextval),
            multiauth=context,
            login_error=login_error,
            authenticator_login_url=url_concat(
                self.authenticator.login_url(self.hub.base_url),
                {'next': nextval},
            ),
        )

    @gen.coroutine
    def get(self):
        """
        Simplify rendering as there is no username
        """
        self.statsd.incr('login.request')
        user = self.get_current_user()
        if user:
            # set new login cookie
            # because single-user cookie may have been cleared or incorrect
            self.set_login_cookie(self.get_current_user())
            self.redirect(self.get_next_url(user), permanent=False)
        else:
            self.finish(self._render())

    @gen.coroutine
    def post(self):
        """
        Redirect to the handler for the appropriate oauth selected
        """
        concat_data = {
            'next': self.get_argument('next', ''),
        }
        if self.authenticator.enable_google and self.get_argument('login_google', None):
            login_url = '{}://{}{}google/login'.format(self.request.protocol, self.request.host, self.hub.base_url)
            self.redirect(url_concat(login_url, concat_data))
        elif self.authenticator.enable_github and self.get_argument('login_github', None):
            login_url = '{}://{}{}github/login'.format(self.request.protocol, self.request.host, self.hub.base_url)
            self.redirect(url_concat(login_url, concat_data))
        elif self.authenticator.enable_nih and self.get_argument('login_nih', None):
            login_url = '{}://{}{}nih/login'.format(self.request.protocol, self.request.host, self.hub.base_url)
            self.redirect(url_concat(login_url, concat_data))
        else:
            html = self._render(login_error='Unknown or missing authenticator')
            self.finish(html)


class MultiLogoutHandler(LogoutHandler):
    pass


class MultiAuthenticator(Authenticator):

    enable_google = Bool(True, help='Enable oauth2 authorization to google').tag(config=True)
    enable_github = Bool(True, help='Enable oauth2 authorization to github').tag(config=True)
    enable_nih = Bool(True, help='Enable CAS/SAML authentication to NIH Login').tag(config=True)

    google_class = Type(GoogleOAuthenticator, Authenticator, help='Must be an authenticator').tag(config=True)
    github_class = Type(GitHubOAuthenticator, Authenticator, help='Must be an authenticator').tag(config=True)
    nih_class = Type(CASAuthenticator, Authenticator, help='Must be an authenticator').tag(config=True)

    google_authenticator = Instance(Authenticator)
    github_authenticator = Instance(Authenticator)
    nih_authenticator = Instance(Authenticator)

    @default('google_authenticator')
    def _default_google_authenticator(self):
        return self.google_class()

    @default('github_authenticator')
    def _default_github_authenticator(self):
        return self.github_class()

    @default('nih_authenticator')
    def _default_nih_authenticator(self):
        return self.nih_class()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.__client_id = None
        self.__client_secret = None
        self.__scope = None

    @property
    def client_id(self):
        return self.__client_id

    @property
    def client_secret(self):
        return self.__client_secret

    @property
    def scope(self):
        return self.__scope

    def set_oauth_tokens(self, subauth):
        """
        Caches configured information from the subauthenticator in properties
        """
        self.__client_id = subauth.client_id
        self.__client_secret = subauth.client_secret
        self.__scope = subauth.scope

    def get_callback_url(self, handler=None):
        """
        This is called by oauth2, it thinks that there will just be one 
        """
        pdb.set_trace()
        if handler is None:
            raise ValueError("MultiAuthenticator only works with a handler")
        if isinstance(handler, GoogleLoginHandler):
            self.set_oauth_tokens(self.google_authenticator)
            if self.google_authenticator.oauth_callback_url:
                return self.google_authenticator.oauth_callback_url
        if isinstance(handler, GitHubLoginHandler):
            self.set_oauth_tokens(self.github_authenticator)
            if self.config.github_authenticator.oauth_callback_url:
                return self.config.github_authenticator.oauth_callback_url
        parts = urlsplit(handler.request.uri)
        callback_url = '{}://{}{}'.format(
            handler.request.protocol,
            handler.request.host,
            parts.path.replace('/login', '/callback')
        )
        return callback_url

    def validate_username(self, username):
        return super().validate_username(username)

    def normalize_username(self, username):
        return super().normalize_username(username)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


    def get_handlers(self, app):
        h = [
            ('/login', MultiLoginHandler),
            ('/logout', MultiLogoutHandler),
        ]
        if self.enable_google:
            handlers = dict(self.google_authenticator.get_handlers(app))
            h.extend([
                ('/google/login', handlers['/oauth_login']),
                ('/google/callback', handlers['/oauth_callback'])
            ])
        if self.enable_github:
            handlers = dict(self.github_authenticator.get_handlers(app))
            h.extend([
                ('/github/login', handlers['/oauth_login']),
                ('/github/callback', handlers['/oauth_callback']),
            ])
        if self.enable_nih:
            handlers = dict(self.nih_authenticator.get_handlers(app))
            h.extend([
                ('/nih/login', handlers['/login']),
            ])
        return h

    @gen.coroutine
    def authenticate(self, handler, data):
        """
        Delegate authentication to the appropriate authenticator
        """
        pdb.set_trace()
        if isinstance(handler, GoogleOAuthHandler):
            return self.google_authenticator.authenticate(handler, data)
        elif isinstance(handler, CASLoginHandler):
            return self.nih_authenticator.authenticate(handler, data)
        else:
            return self.github_authenticator.authenticate(handler, data)