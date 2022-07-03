from jupyterhub.auth import DummyAuthenticator
from modules.MultiAuthenticator import MultiAuthenticator
import os

# Generic
c.JupyterHub.admin_access = True
c.Spawner.default_url = '/lab'
c.JupyterHub.base_url = '/newhub/'

# Set log level
c.Application.log_level = "DEBUG"

# Add an admin user for testing the admin page
c.Authenticator.admin_users = {"admin"}

# Enable auth state to pass the authentication dictionary
# auth_state to ths spawner
c.Authenticator.enable_auth_state = False

# Set the LTI 1.1 authenticator.
c.JupyterHub.authenticator_class = MultiAuthenticator

c.JupyterHub.admin_users = {"admin"}

# Docker spawner

#c.JupyterHub.authenticator_class = 'ltiauthenticator.LTIAuthenticator'
#c.LTIAuthenticator.consumers = {
    #"client-key": "client-secret"
#}

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