from urllib.parse import urlsplit, urlencode
import os

from tornado import gen
from tornado.escape import url_escape
from tornado.httputil import url_concat

from traitlets import (
    Unicode, Integer, Dict, TraitError, List, Bool, Any,
    Type, Set, Instance, Bytes, Float,
    observe, default
)

from jupyterhub.auth import Authenticator
from jupyterhub.handlers.login import LoginHandler, LogoutHandler
from jupyterhub.utils import maybe_future

from oauthenticator.oauth2 import OAuthLoginHandler, OAuthenticator
from oauthenticator.generic import GenericOAuthenticator
from ltiauthenticator import LTIAuthenticator, LTIAuthenticateHandler

class MultiLoginHandler(LoginHandler):

    async def get(self):
        """
        Simplify rendering as there is no username
        """
        self.statsd.incr('login.request')
        user = await maybe_future(self.get_current_user())
        if user:
            # set new login cookie
            # because single-user cookie may have been cleared or incorrect
            self.set_login_cookie(self.get_current_user())
            self.redirect(self.get_next_url(user), permanent=False)
        else:
            self.finish(self._render())

class KeycloakLogoutHandler(LogoutHandler):
    kc_logout_url = os.environ.get("KEYCLOAK_LOGOUT_URL", "")

    async def get(self):
        # redirect to keycloak logout url and redirect back with kc=true parameters
        # then proceed with the original logout method.
        logout_kc = self.get_argument('kc', '')
        if logout_kc != 'true':
            logout_url = self.request.full_url() + '?kc=true'
            self.redirect(self.kc_logout_url + '?' + urlencode({ 'redirect_uri' : logout_url}))
        else:
            await super().get()

class MultiAuthenticator(Authenticator):

    enable_keycloak = Bool(True, help='Enable oauth2 authorization to keycloak').tag(config=True)
    enable_lti = Bool(True, help='Enable lti authorization to learn').tag(config=True)

    keycloak_class = Type(GenericOAuthenticator, OAuthenticator, help='Must be an GenericOAuthenticator').tag(config=True)
    lti_class = Type(LTIAuthenticator, Authenticator, help='Must be an authenticator').tag(config=True)

    keycloak_authenticator = Instance(OAuthenticator)
    lti_authenticator = Instance(Authenticator)

    @default('keycloak_authenticator')
    def _default_keycloak_authenticator(self):
        return self.keycloak_class()

    @default('lti_authenticator')
    def _default_lti_authenticator(self):
        return self.lti_class()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.__client_id = None
        self.__client_secret = None
        self.__consumers = None
        self.__authorize_url = None
        self.__scope = None
    
    @property
    def authorize_url(self):
        return self.__authorize_url

    @property
    def client_id(self):
        return self.__client_id

    @property
    def client_secret(self):
        return self.__client_secret
    
    @property
    def consumers(self):
        return self.__consumers

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
        self.__authorize_url = subauth.authorize_url

    def get_callback_url(self, handler=None):
        """
        called by oauth2
        """
        if handler is None:
            raise ValueError("MultiAuthenticator only works with a handler")
        if isinstance(handler, OAuthLoginHandler):
            self.set_oauth_tokens(self.keycloak_authenticator)
            if self.keycloak_authenticator.oauth_callback_url:
                return self.keycloak_authenticator.oauth_callback_url
        parts = urlsplit(handler.request.uri)
        callback_url = '{}://{}{}'.format(
            handler.request.protocol,
            handler.request.host,
            parts.path.replace('/login', '/callback')
        )
        return callback_url
    

    def get_handlers(self, app):
        h = [
            ('/login', MultiLoginHandler),
            ('/logout', KeycloakLogoutHandler),
        ]
        if self.enable_keycloak:
            handlers = dict(self.keycloak_authenticator.get_handlers(app))
            h.extend([
                ('/keycloak/login', handlers['/oauth_login']),
                ('/keycloak/callback', handlers['/oauth_callback'])
            ])
        if self.enable_lti:
            handlers = dict(self.lti_authenticator.get_handlers(app))
            h.extend([
                ('/lti/launch', handlers['/lti/launch'])
            ])
        return h

    async def authenticate(self, handler, data):
        """
        Delegate authentication to the appropriate authenticator
        """
        if isinstance(handler, LTIAuthenticateHandler):
            return await maybe_future(self.lti_authenticator.authenticate(handler, data))
        else:
            return await maybe_future(self.keycloak_authenticator.authenticate(handler, data))