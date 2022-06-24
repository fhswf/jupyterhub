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
c.DummyAuthenticator.admin_users = {'admin'}
c.Authenticator.admin_users = {'admin'}
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