import logging
from jupyterhub.auth import DummyAuthenticator
from modules.MultiAuthenticator import MultiAuthenticator
import os
import sys
import docker

from modules.CustomSpawner import CustomSpawner

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
    # c.SwarmSpawner.allowed_images = os.environ['DOCKER_JUPYTER_CONTAINERS'].split(",")
    # c.SwarmSpawner.debug = True
    # network_name = os.environ['DOCKER_NETWORK_NAME']
    # c.SwarmSpawner.network_name = network_name
    # c.SwarmSpawner.extra_host_config = {'network_mode': network_name}
    # c.SwarmSpawner.extra_placement_spec = { 'constraints' : ['node.role==worker'] }
    raise Exception("Please use modules.CustomSpawner.CustomSpawner instead of {}".format(os.environ['JUPYTERHUB_SPAWNERCLASS']))

elif  os.environ['JUPYTERHUB_SPAWNERCLASS'] == 'dockerspawner.DockerSpawner':
    c.DockerSpawner.network_name = os.environ['DOCKER_NETWORK_NAME']
    #c.DockerSpawner.image = os.environ['DOCKER_JUPYTER_CONTAINER']
    c.DockerSpawner.allowed_images = os.environ['DOCKER_JUPYTER_CONTAINERS'].split(",") 

elif  os.environ['JUPYTERHUB_SPAWNERCLASS'] == 'modules.CustomSpawner.CustomSpawner':
    if "DOCKER_JUPYTER_CONTAINERS" in os.environ:
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
if "HUB_IP" in os.environ:
    hub_ip = os.environ.get('HUB_IP')
    c.JupyterHub.hub_ip = os.environ['HUB_IP']
if "HUB_CONNECT_IP" in os.environ:
    c.JupyterHub.hub_connect_ip = os.environ['HUB_CONNECT_IP']
c.JupyterHub.shutdown_on_logout = True
if "LAB_HUB_API_URL" in os.environ:
    c.Spawner.hub_connect_url = os.environ['LAB_HUB_API_URL']

# user data persistence
# -> https://github.com/jupyterhub/dockerspawner#data-persistence-and-dockerspawner
notebook_dir = os.environ.get('DOCKER_NOTEBOOK_DIR') or '/home/jovyan/work'
c.DockerSpawner.notebook_dir = notebook_dir
if "VOLUME_PATH_PREFIX" in os.environ:
    mount_prefix = os.environ.get('VOLUME_PATH_PREFIX')
else:
    mount_prefix = "userdata"
c.DockerSpawner.volumes = {
    '/mnt/nfs_share/docker/jupyterhub/' + mount_prefix + '/jupyterhub-user-{username}/_data': notebook_dir, 
    '/mnt/nfs_share/docker/jupyterhub/' + mount_prefix + '/jupyterhub-user-{username}/home_data': '/home/{username}'
}
#c.Spawner.env_keep = ['LD_LIBRARY_PATH'] # set in DOCKERFILE of spawned container 

#===========================================================================
#                            GPU Stuff
#===========================================================================
# TODO make this dependend on user/moodle/group, also this does noting for swarm deployment
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
if "SPAWNER_CPU_LIMIT" in os.environ:
    c.Spawner.cpu_limit = os.environ['SPAWNER_CPU_LIMIT']
else:
    c.Spawner.cpu_limit = 16
    print('SPAWNER_CPU_LIMIT not set in .env file')

if "SPAWNER_MEM_LIMIT" in os.environ:
    c.Spawner.mem_limit = os.environ['SPAWNER_MEM_LIMIT']
else:
    c.Spawner.mem_limit = '40G'
    print('SPAWNER_MEM_LIMIT not set in .env file')

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
