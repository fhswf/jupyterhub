import grp
import pwd
from typing import Any, Dict, List, Tuple
from dockerspawner import SwarmSpawner
from docker.types import Mount 
import os
from traitlets import (
    default
)
import threading

_my_swarm_gpus_snap =  {}
_my_spawn_status = {"count": 0, "gpu_flat": None}
_my_lock = threading.Lock()

def update_gpus(gpus: Dict[Any, List]) -> None:
    global _my_swarm_gpus_snap 
    global _my_spawn_status
    if gpus != _my_swarm_gpus_snap:
        _my_swarm_gpus_snap = gpus 
        _my_spawn_status.update({"gpu_flat": ([(k, gpu) for k, v in _my_swarm_gpus_snap.items() for gpu in v])})

def add_gpu_spawn() -> Tuple[str, str]:
    """
    returns:
        Tuple[str, str] of node_id and gpu_id
    """
    global _my_lock
    global _my_spawn_status
    with _my_lock:
        old = _my_spawn_status.get("count")
        _my_spawn_status.update({"count": old + 1})
    return _my_spawn_status.get("gpu_flat")[_my_spawn_status.get("count") % len(_my_spawn_status.get("gpu_flat"))]
     
def rm_gpu_spawn() -> None:
    global _my_lock
    global _my_spawn_status
    with _my_lock:
        old = _my_spawn_status.get("count")
        _my_spawn_status.update({"count": old - 1})


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
        """
        get called prior to self.docker("create_service", ...) or self.docker("create_container", ...)
        """
        print("==============GET ENV=================")
        ret = super().get_env(*args, **kwargs)
        print(ret)
        return ret
    

    @default('options_form')
    def _default_options_form(self):
        allowed_images = self._get_allowed_images()
        if len(allowed_images) <= 1:
            # default form only when there are images to choose from
            return ''
        # form derived from wrapspawner.ProfileSpawner

        # self._custom_extra_config
        # TODO maybe use this stuff here

        image_option_t = '<option value="{image}" {selected}>{image}</option>'
        image_options = [
            image_option_t.format(
                image=image, selected='selected' if image == self.image else ''
            )
            for image in allowed_images
        ]
        gpu_options_t = '<option value="{gpu}">{gpu}</option>'
        gpu_options =[
            gpu_options_t.format(
                gpu=gpu
            )
            for gpu in ["gpu-1", "gpu-2", "gpu-3", "gpu-4"]
        ]
        return """
        <label for="image">Select an image and a GPU to use</label>
        <select class="form-control" name="image" required autofocus>
        {image_options}
        </select><div><br/></div>
        <label for="image">Select an image and a GPU to use</label>
        <select class="form-control" name="gpu">
        {gpu_options}
        </select>    
        """.format(
            image_options=image_options,
            gpu_options=gpu_options 
        )

    def options_from_form(self, formdata):
        """
        Turn options formdata into user_options
        options can be retrieved in the spawner via Dict: self.user_options 
        """
        options = {}
        if 'image' in formdata:
            options['image'] = formdata['image'][0]
        if 'gpu' in formdata:
            options['gpu'] = formdata['gpu'][0]

        #options['hostname'] = formdata['hostname']
        #hostname = ''.join(formdata['hostname'])
        #self.extra_placement_spec = { 'constraints' : ['node.hostname==' + hostname] }
        return options

    async def pre_spawn_hook(self, spawner):
        """
        get called prior to self.docker("create_service", ...) or self.docker("create_container", ...)
        designed to containe blocking operations 
        gets called before the container actau 
        Alternatively you can do this in the config
        def my_hook(spawner):
            username = spawner.user.name
        c.Spawner.pre_spawn_hook = my_hook
        """
        print("================ run pre_spawn_hook ================")
        username = spawner.user.name
        print(username, spawner.user)
        # make sure we cant mount nfs_share
        # key is source outside container, val is target inside container
        mounts : List[str]
        with open("/proc/mounts", "r") as f:
            mounts = f.readlines()

        def _check_mount_point(lines, substring):
            for line in lines:
                split_line = line.split(" ")
                if substring.startswith(split_line[1]): # and split_line[2].startswith("nfs")?
                    return True
            raise FileNotFoundError("can not find mounted volume directory, {}".format(substring))
            

        for key, value in spawner.volumes.items():
            spawner.volumes[key] = self.format_string(value)
            mount_point = spawner.format_volume_name(key, self)
            # absolute bind poath start with /
            if mount_point.startswith("/") and _check_mount_point(mounts, mount_point):
                if not os.path.exists(mount_point):
                    os.makedirs(mount_point)
                    uid = pwd.getpwnam("root").pw_uid
                    gid = grp.getgrnam("users").gr_gid
                    os.chown(mount_point, uid, gid)
                    os.chmod(mount_point, 0o775)
                    

        # TODO make image selection more sophisticated        
        if "gpu" in self.user_options["image"]:
            
            gpus = {} # get aviable gpus. TODO maybe cache this?
            for swarm_node in spawner._custom_extra_config["swarm_nodes"]:
                id = swarm_node["ID"]
                gpus.update({id: []})
                if "Resources" in swarm_node:
                    if "GenericResources" in swarm_node["Resources"]:
                        for r in swarm_node["Resources"]["GenericResources"]:
                            if "NamedResourceSpec" in r and r["NamedResourceSpec"]["Kind"] == "NVIDIA-GPU":
                                gpus[id].append(r["NamedResourceSpec"]["Value"])
                                       
            update_gpus(gpus)
            _id, gpu = add_gpu_spawn()
            print(_id, gpu)
            self.extra_placement_spec.update({ 'constraints' : ['node.role==worker', "node.id=={}".format(_id)] }) # TODO replace worker with gpu label
            self.environment.update({"NVIDIA_VISIBLE_DEVICES": gpu})
            print(self.extra_placement_spec)
            print(self.environment)
        else:
            self.environment.update({"NVIDIA_VISIBLE_DEVICES": "void"})
        self.extra_container_spec.update({"user": "root"})
        #m = Mount()
        #self.extra_container_spec.get("mounts").append()
        #self.extra_resources_spec.update({"generic_resources": {"NVIDIA-GPU":1}})  # TODO so far we dont know how to make this work
        
        # gpu node have default runtime set as nvidia, which behaves like runc without gpu envs 
        # see here https://docker-py.readthedocs.io/en/stable/api.html#docker.types.TaskTemplate
        # self.extra_create_kwargs.update({ "runtime": "nvidia"}) # does not work for swarm
        

    async def post_spawn_hook(self, spawner):
        """
        Runs after the spawner removes the service/container
        """
        if "gpu" in self.user_options["image"]:
            rm_gpu_spawn()