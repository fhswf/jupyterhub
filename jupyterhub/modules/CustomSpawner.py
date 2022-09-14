import grp
import pwd
from typing import Any, Dict, List, Tuple
from dockerspawner import SwarmSpawner
from docker.types import Mount 
from tornado import web
from docker.models.images import Image
import os
from jupyterhub.utils import maybe_future
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

    def get_env(self, *args, **kwargs):
        """
        get called prior to self.docker("create_service", ...) or self.docker("create_container", ...)
        """
        ret = super().get_env(*args, **kwargs)
        return ret

    # override
    async def get_options_form(self):
        """Get the options form
        Returns:
          Future (str): the content of the options form presented to the user
          prior to starting a Spawner.
        .. versionadded:: 0.9
        """
        if callable(self.options_form):
            options_form = await maybe_future(self.options_form(self))
        else:
            options_form = self.options_form
        
        return await self.call_options_form(options_form)

    # override
    async def check_allowed(self, image):
        print("====== call check_allowed =======")
        _allowed_images = {}
        try:
            if len(self._images) > 0:
                for i in self._images:
                    if i["RepoTags"][0] != "<none>:<none>":
                        _allowed_images.update({i["RepoTags"][0]:i["RepoTags"][0]})
        except:
            pass
        allowed_images = self._get_allowed_images()
        if not allowed_images:
            return image
        else:
            allowed_images.update(_allowed_images) # join givin dict with found images
        if image not in allowed_images:
            raise web.HTTPError(
                400,
                "Image %s not in allowed list: %s" % (image, ', '.join(allowed_images)),
            )
        # resolve image alias to actual image name
        return allowed_images[image]
    
    # override
    @default('options_form')
    def _default_options_form(self):    
        print("=== call _default_options_form ===")
        _allowed_images = self._get_allowed_images()
        image_option_t = '<option value="{image}" {selected}>{image}</option>'
        image_options = [
            image_option_t.format(
                image=image, selected='selected' if image == self.image else ''
            )
            for image in _allowed_images
        ]

        gpu_options_t = '<option value="{gpu}">{gpu}</option>'
        gpu_options =[
            gpu_options_t.format(
                gpu=gpu
            )
            for gpu in ["yes", "no"]
        ]
        return """ <label for="image">Select an image and a GPU to use</label>
            <select class="form-control" name="image" required autofocus>
            {image_options}
            </select>
            <div><br/></div>
            <label for="image">Do you want to have a gpu?</label>
            <select class="form-control" name="gpu">
            {gpu_options}
            </select>  
        """.format(image_options=image_options, gpu_options=gpu_options)


    def _custom_options_form(self, _images, id_filter=None):
        print("===== call _custom_options_form ======")
        images = []
        for i in _images:
            if i["RepoTags"][0] == "<none>:<none>":
                continue
            if id_filter:
                if i["Labels"]["fhswf.jupyterhub.moodle.course.id"] == id_filter:
                    images.append(i["RepoTags"][0])
            else:
                images.append(i["RepoTags"][0])
                    
        image_option_t = '<option value="{image}" {selected}>{image}</option>'
        image_options = [
            image_option_t.format(
                image=image, selected='selected' if image == self.image else ''
            )
            for image in images
        ]
        image_selection = """
            <label for="image">Select an image and a GPU to use</label>
            <select class="form-control" name="image" required autofocus>
            {options}
            </select>
        """.format(options=image_options)
        return image_selection


    async def call_options_form(self, default_form):
        print("====== call call_options_form =======")
        auth_state = await self.user.get_auth_state()
        images = []
        _images = await self.docker("images", filters={"label":"fhswf.jupyterhub.runtime"})
        if isinstance(_images, list):
            for i in _images:
                images.append(i)
        else:
            if isinstance(_images, Image):
                images.append(_images)
        self._images = images

        def _default_image_select(id_filter=None):
            if len(images) > 0:
                return self._custom_options_form(images, id_filter)
            else:
                return default_form

        if "lti_version" in auth_state and auth_state["lti_version"].startswith("LTI"):
            if "context_id" in auth_state:
                course_id = auth_state["context_id"]
                self._lti_course_id = course_id
                # find all iamges with courseid still 
                image_names = [a for a in images if 
                        "Labels" in a and 
                        a["Labels"] is not None and 
                        a["Labels"]["fhswf.jupyterhub.moodle.course.id"] == course_id and 
                        a["RepoTags"][0] != "<none>:<none>" and
                        "fhswf.jupyterhub.runtime" in a["Labels"].keys()]

                if len(image_names) == 1:
                    self.image =  image_names[0]["RepoTags"][0]
                    if image_names[0]["Labels"]["fhswf.jupyterhub.runtime"] == "NVIDIA-GPU":
                        self._use_gpu = True
                    elif image_names[0]["Labels"]["fhswf.jupyterhub.runtime"] == "CPU":
                        self._use_gpu = False
                    else:
                        self._use_gpu = False
                    return ''
                elif len(image_names) > 1:
                    return _default_image_select(id_filter=course_id)
                else:
                    return _default_image_select()
            else:
                return _default_image_select()
            
        elif "scope" in auth_state and "openid" in auth_state["scope"]: 
            return _default_image_select()

        else:
            raise web.HTTPError(405, "Could not determine login type")
    

    # override
    def options_from_form(self, formdata):
        """
        Turn options formdata into user_options
        options can be retrieved in the spawner via Dict: self.user_options 
        """
        print("====== call options_from_form =======")
        options = {}
        if 'image' in formdata:
            options['image'] = formdata['image'][0]

        if 'gpu' in formdata:
            options['gpu'] = formdata['gpu'][0]
        else:
            image_names = [a for a in self._images if a["RepoTags"][0]== "jupyterlab_testimg-gpu:latest"]
            if len(image_names) == 1:
                if image_names[0]["Labels"]["fhswf.jupyterhub.runtime"] == "NVIDIA-GPU":
                    options['gpu'] = "yes"
                elif image_names[0]["Labels"]["fhswf.jupyterhub.runtime"] == "CPU":
                    options['gpu'] = "no"
                else:
                    options['gpu'] = "no"
            elif len(image_names) == 0:
                raise web.HTTPError(500, "Could not resolve docker image, image not found")
            else:
                raise web.HTTPError(500, "Could not resolve docker image, imagename ambiguous")
        #options['hostname'] = formdata['hostname']
        #hostname = ''.join(formdata['hostname'])
        #self.extra_placement_spec = { 'constraints' : ['node.hostname==' + hostname] }
        return options

    # override
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
        print("====== call pre_spawn_hook =======")
        username = spawner.user.name
        print(username)
        print(spawner.user.get_auth_state())
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

        # TODO redo form and then change this...
        if self.user_options is not None and "gpu" in self.user_options and "yes" in self.user_options["gpu"] or self._use_gpu:
            gpus = {} 
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
            self.extra_placement_spec.update({ 'constraints' : ['node.role==worker', "node.id=={}".format(_id)] }) # TODO replace worker with gpu label
            self.environment.update({"NVIDIA_VISIBLE_DEVICES": gpu})
            self.environment.update({"NVIDIA_DRIVER_CAPABILITIES": "compute,utility"})
            self.environment.update({"NVIDIA_REQUIRE_CUDA": "cuda>=11"})

        else:
            self.environment.update({"NVIDIA_VISIBLE_DEVICES": "void"})
        self.extra_container_spec.update({"user": "root"})
        #m = Mount()
        #self.extra_container_spec.get("mounts").append()
        #self.extra_resources_spec.update({"generic_resources": {"NVIDIA-GPU":1}})  # TODO so far we dont know how to make this work
        
        # gpu node have default runtime set as nvidia, which behaves like runc without gpu envs 
        # see here https://docker-py.readthedocs.io/en/stable/api.html#docker.types.TaskTemplate
        # self.extra_create_kwargs.update({ "runtime": "nvidia"}) # does not work for swarm
        
    # override
    async def post_spawn_hook(self, spawner):
        """
        Runs after the spawner removes the service/container
        """
        if "gpu" in self.user_options["image"]:
            rm_gpu_spawn()