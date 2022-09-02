import logging
from jupyterhub.auth import DummyAuthenticator
from modules.MultiAuthenticator import MultiAuthenticator
import os
import sys
import docker

#===========================================================================
#                            General Configuration
#===========================================================================

c.JupyterHub.admin_access = True
c.JupyterHub.template_paths = ['templates']
c.Application.log_level = "DEBUG"
c.JupyterHub.log_level = logging.DEBUG

c.Spawner.default_url = '/lab'
c.JupyterHub.base_url = os.environ['HUB_BASE_URL_PREFIX'] + "/"

c.Authenticator.admin_users = {"admin"}

# Enable auth state to pass the authentication dictionary
# auth_state to the spawner
c.Authenticator.enable_auth_state = True

# Set the MultiAuthenticator as the authenticator
c.JupyterHub.authenticator_class = MultiAuthenticator


#===========================================================================
#                            Docker Spawner Configuration
#===========================================================================

c.JupyterHub.spawner_class = os.environ['JUPYTERHUB_SPAWNERCLASS']
print("Starting with Spawnerclass: {}".format(os.environ['JUPYTERHUB_SPAWNERCLASS']))

if os.environ['JUPYTERHUB_SPAWNERCLASS'] == "dockerspawner.SwarmSpawner":
    c.SwarmSpawner.allowed_images = os.environ['DOCKER_JUPYTER_CONTAINERS'].split(",")
    c.SwarmSpawner.debug = True
    network_name = os.environ['DOCKER_NETWORK_NAME']
    c.SwarmSpawner.network_name = network_name
    c.SwarmSpawner.extra_host_config = {'network_mode': network_name}


elif  os.environ['JUPYTERHUB_SPAWNERCLASS'] == 'dockerspawner.DockerSpawner':
    c.DockerSpawner.network_name = os.environ['DOCKER_NETWORK_NAME']
    #c.DockerSpawner.image = os.environ['DOCKER_JUPYTER_CONTAINER']
    c.DockerSpawner.allowed_images = os.environ['DOCKER_JUPYTER_CONTAINERS'].split(",") 

elif  os.environ['JUPYTERHUB_SPAWNERCLASS'] == 'modules.CustomSpawner.CustomSpawner':
    c.Spawner.allowed_images = os.environ['DOCKER_JUPYTER_CONTAINERS'].split(",")
    c.Spawner.debug = True
    network_name = os.environ['DOCKER_NETWORK_NAME']
    c.Spawner.network_name = network_name
    c.Spawner.extra_host_config = {'network_mode': network_name}
else:
    raise Exception("illegal spawner class found in config {}".format(os.environ['JUPYTERHUB_SPAWNERCLASS']))


if "DOCKER_PERSIST_NOTEBOOK" in os.environ.keys():
    c.Spawner.remove = not os.environ['DOCKER_PERSIST_NOTEBOOK']
else:
    c.Spawner.remove = True

c.Spawner.http_timeout=120
c.Spawner.start_timeout=300

# -> https://github.com/jupyterhub/dockerspawner/blob/master/examples/oauth/jupyterhub_config.py
c.JupyterHub.hub_ip = os.environ['HUB_IP']
c.JupyterHub.shutdown_on_logout = True

# user data persistence
# -> https://github.com/jupyterhub/dockerspawner#data-persistence-and-dockerspawner
notebook_dir = os.environ.get('DOCKER_NOTEBOOK_DIR') or '/home/jovyan/work'
c.DockerSpawner.notebook_dir = notebook_dir
#c.DockerSpawner.volumes = {'jupyterhub-user-{username}': notebook_dir}
#c.Spawner.env_keep = ['LD_LIBRARY_PATH'] # set in DOCKERFILE of spawned container 
def cumpute_env_value(spwner_instance):
    print("==================0envcall=============")
    logging.warning("==================0envcall=============")
    print(spwner_instance.__dict__)
    logging.warning(spwner_instance.__dict__)
    return "1"

c.Spawner.env_keep = ["NVIDIA_VISIBLE_DEVICES"]
c.Spawner.environment = {
    'NB_USER': "${JUPYTERHUB_USER}", 
    'CHOWN_HOME': 'yes',
    "NVIDIA_VISIBLE_DEVICES": cumpute_env_value
    }
c.SwarmSpawner.env_keep = ["NVIDIA_VISIBLE_DEVICES"]
c.SwarmSpawner.environment = {
    'NB_USER': "${JUPYTERHUB_USER}", 
    'CHOWN_HOME': 'yes',
    "NVIDIA_VISIBLE_DEVICES": cumpute_env_value
    }
c.DockerSpawner.env_keep = ["NVIDIA_VISIBLE_DEVICES"]
c.DockerSpawner.environment = {
    'NB_USER': "${JUPYTERHUB_USER}", 
    'CHOWN_HOME': 'yes',
    "NVIDIA_VISIBLE_DEVICES": cumpute_env_value
    }



# what is this for? we cant use it with swarm as create_service() from docker.py does not allow this argument
# c.DockerSpawner.extra_create_kwargs = {"user": "root"}

#===========================================================================
#                            GPU Stuff
#===========================================================================
# TODO make this dependend on user/moodle/group
c.DockerSpawner.extra_host_config = {
    "runtime": "nvidia",
    "device_requests": [
        docker.types.DeviceRequest(
            count=1,
            capabilities=[["gpu"]],
        ),
    ],
}

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