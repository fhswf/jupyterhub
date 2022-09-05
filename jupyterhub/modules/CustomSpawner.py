from dockerspawner import SwarmSpawner
import os

class CustomSpawner(SwarmSpawner):
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        print("==============INIT SPAWNER=================")
        """
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
        """
    def get_env(self, *args, **kwargs):
        print("==============GET ENV=================")

        ret = super().get_env(*args, **kwargs)
        ret.update({"NVIDIA_VISIBLE_DEVICES": "1"})
        print(ret)
        return ret
    

    # Shows frontend form to user for host selection
    # The option values should correspond to the hostnames
    # that appear in the `docker node ls` command output
    def _options_form_default(self):
        return """
        <label for="hostname">Select your desired host</label>
        <select name="hostname" size="1">
            <option value="node1">node1 - GPU: RTX 2070 / CPU: 40</option>
            <option value="node2">node2 - GPU: GTX 1080 / CPU: 32</option>
        </select>
        """

    # Retrieve the selected choice and set the swarm placement constraints
    def options_from_form(self, formdata):
        options = {}
        options['hostname'] = formdata['hostname']
        hostname = ''.join(formdata['hostname'])
        self.extra_placement_spec = { 'constraints' : ['node.hostname==' + hostname] }
        return options
