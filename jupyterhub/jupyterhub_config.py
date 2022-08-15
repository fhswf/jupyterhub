from jupyterhub.auth import DummyAuthenticator
from modules.MultiAuthenticator import MultiAuthenticator
import os
import sys


#===========================================================================
#                            General Configuration
#===========================================================================

c.JupyterHub.admin_access = True
c.JupyterHub.template_paths = ['templates']
c.Application.log_level = "DEBUG"

c.Spawner.default_url = '/lab'
c.JupyterHub.base_url = '/newhub/'

c.Authenticator.admin_users = {"admin"}

# Enable auth state to pass the authentication dictionary
# auth_state to the spawner
c.Authenticator.enable_auth_state = True

# Set the MultiAuthenticator as the authenticator
c.JupyterHub.authenticator_class = MultiAuthenticator


#===========================================================================
#                            Docker Spawner Configuration
#===========================================================================

c.JupyterHub.spawner_class = 'dockerspawner.DockerSpawner'
c.DockerSpawner.network_name = os.environ['DOCKER_NETWORK_NAME']
#c.DockerSpawner.image = os.environ['DOCKER_JUPYTER_CONTAINER']
c.DockerSpawner.allowed_images = os.environ['DOCKER_JUPYTER_CONTAINERS'].split(",")
c.Spawner.http_timeout=60
c.Spawner.start_timeout=300
#[
#    "jupyterlab_img",
#    "ghcr.io/fhswf/jupyterhub/jupyterlab-scipy-gpu:main",
#    "ghcr.io/fhswf/jupyterhub/jupyterlab-scipy-cpu:main"
#]

# -> https://github.com/jupyterhub/dockerspawner/blob/master/examples/oauth/jupyterhub_config.py
c.JupyterHub.hub_ip = os.environ['HUB_IP']

c.JupyterHub.shutdown_on_logout = True

# user data persistence
# -> https://github.com/jupyterhub/dockerspawner#data-persistence-and-dockerspawner
notebook_dir = os.environ.get('DOCKER_NOTEBOOK_DIR') or '/home/jovyan/work'
c.DockerSpawner.notebook_dir = notebook_dir
c.DockerSpawner.volumes = {'jupyterhub-user-{username}': notebook_dir}
c.DockerSpawner.environment = {
    'NB_USER': '${JUPYTERHUB_USER}', 
    'CHOWN_HOME': 'yes'}
c.DockerSpawner.extra_create_kwargs = {"user": "root"}

#===========================================================================
#                            GPU Stuff
#===========================================================================
c.DockerSpawner.extra_host_config = {"runtime": "nvidia"}
c.Spawner.args = ["--gpus all"]

#===========================================================================
#                            Other Configuration
#===========================================================================

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
    },
    {
        "name": "jupyterhub-idle-culler-role",
        "scopes": [
            "list:users",
            "read:users:activity",
            "read:servers",
            "delete:servers",
            # "admin:users", # if using --cull-users
        ],
        # assignment of role's permissions to:
        "services": ["jupyterhub-idle-culler-service"],
    }
]

c.JupyterHub.services = [
    {
        "name": "jupyterhub-idle-culler-service",
        "command": [
            sys.executable,
            "-m", "jupyterhub_idle_culler",
            "--timeout=3600",
        ],
        # "admin": True,
    }
]