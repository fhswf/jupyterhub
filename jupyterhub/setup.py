from setuptools import setup, find_packages

setup(
    name='Modules',
    version='1.0.0',
    packages=find_packages(include=['modules', 'modules.*'])
)