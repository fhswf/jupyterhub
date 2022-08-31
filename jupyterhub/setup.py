from setuptools import setup, find_packages

setup(
    name='Modules',
    version='1.0.0',
    packages=find_packages(include=['modules', 'modules.*']),
    #entry_points={ # see here: https://jupyterhub.readthedocs.io/en/stable/reference/spawners.html#registering-custom-spawners-via-entry-points
    #    'jupyterhub.spawners': [
    #        'CustomSpawner = modules:CustomSpawner', 
    #    ],
    #},
)