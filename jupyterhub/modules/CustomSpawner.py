from dockerspawner import DockerSpawner
import os

class CustomSpawner(DockerSpawner):
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.default_url = '/lab'
        notebook_dir = os.environ.get('DOCKER_NOTEBOOK_DIR') or '/home/jovyan/work'

        self.user_options['cpu_limit'] = 1
        self.user_options['mem_limit'] = '10G'
        self.user_options['extra_host_config'] = {
            "runtime": "nvidia",
            "device_requests": [
                docker.types.DeviceRequest(
                    count=1,
                    capabilities=[["gpu"]],
                ),
            ],
        }
        self.user_options['environment'] = {
            'NB_USER': '${JUPYTERHUB_USER}',
            'CHOWN_HOME': 'yes',
        }
        self.user_options['extra_create_kwargs'] = {"user": "root"}
        self.user_options['start_timeout'] = 300
        self.user_options['http_timeout'] = 120
        self.user_options['shutdown_on_logout'] = True
        self.user_options['notebook_dir'] = notebook_dir
        self.user_options['volumes'] = {'jupyterhub-user-{username}': notebook_dir}
        self.user_options['env_keep'] = ['LD_LIBRARY_PATH'] # set in DOCKERFILE of spawned container
        # self.user_options['image'] = os.environ['DOCKER_JUPYTER_CONTAINER']
        self.user_options['allowed_images'] = os.environ['DOCKER_JUPYTER_CONTAINERS'].split(",")
        self.user_options['network_name'] = os.environ['DOCKER_NETWORK_NAME']

        if "DOCKER_PERSIST_NOTEBOOK" in os.environ.keys():
            c.Spawner.remove = not os.environ['DOCKER_PERSIST_NOTEBOOK']
        else:
            c.Spawner.remove = True