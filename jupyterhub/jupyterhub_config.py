# JupyterHub configuration
#
# If you update this file, do not forget to delete the `jupyterhub_data` volume before restarting the jupyterhub service:
##
# docker volume rm jupyterhub_jupyterhub_data
##
# or, if you changed the COMPOSE_PROJECT_NAME to <name>:
##
# docker volume rm <name>_jupyterhub_data
##

from jupyterhub.auth import DummyAuthenticator
import os

# Generic
c.JupyterHub.admin_access = True
c.Spawner.default_url = '/lab'

# Temporary base_url for testing behind reverse proxy
c.JupyterHub.base_url = '/newhub/'

# Authenticator
c.JupyterHub.authenticator_class = 'dummy'

c.DummyAuthenticator.enable_auth_state = True
c.DummyAuthenticator.admin_users = {'admin', 'lll'}
c.Authenticator.admin_users = {'admin', 'lll'}
c.JupyterHub.admin_users = {"admin"}


"""
GitLab

from oauthenticator.gitlab import GitLabOAuthenticator
c.JupyterHub.authenticator_class = GitLabOAuthenticator
"""

# Docker spawner
c.JupyterHub.spawner_class = 'dockerspawner.DockerSpawner'
c.DockerSpawner.image = os.environ['DOCKER_JUPYTER_CONTAINER']
c.DockerSpawner.network_name = os.environ['DOCKER_NETWORK_NAME']
# -> https://github.com/jupyterhub/dockerspawner/blob/master/examples/oauth/jupyterhub_config.py
c.JupyterHub.hub_ip = os.environ['HUB_IP']

# user data persistence
# -> https://github.com/jupyterhub/dockerspawner#data-persistence-and-dockerspawner
notebook_dir = os.environ.get('DOCKER_NOTEBOOK_DIR') or '/home/user'
c.DockerSpawner.notebook_dir = notebook_dir
c.DockerSpawner.volumes = {'jupyterhub-user-{username}': notebook_dir}
c.DockerSpawner.environment = {
    'NB_USER': '${JUPYTERHUB_USER}', 
    'CHOWN_HOME': 'yes'}
c.DockerSpawner.extra_create_kwargs = {"user": "root"}

# Other stuff
c.Spawner.cpu_limit = 1
c.Spawner.mem_limit = '10G'

c.JupyterHub.load_roles = [
    {
        "name": "server-rights",
        "scopes": [
            "list:users",
            "read:users:activity",
            "read:servers",
            "delete:servers",
                # "admin:users", # if using --cull-users
        ]
        # assignment of role's permissions to:
        # "services": ["jupyterhub-idle-culler-service"],
    }
]

# Services
