**[Technical Overview](#technical-overview)** |
**[Installation](#installation)** |
**[Configuration](#configuration)** |
**[Deployment](#deployment)** |
**[Contributing](#contributing)** |
**[License](#license-mit)**

# Jupyterhub with Docker Swarm and GPUs

[![Docker Image CI](https://github.com/fhswf/jupyterhub/actions/workflows/docker-image-ci.yml/badge.svg?branch=main)](https://github.com/fhswf/jupyterhub/actions/workflows/docker-image-ci.yml)
[![GitHub](https://img.shields.io/badge/issue_tracking-github-blue?logo=github)](https://github.com/fhswf/jupyterhub/issues)
[![GitHub Tags](https://img.shields.io/github/v/tag/fhswf/jupyterhub?style=plastic)](https://github.com/fhswf/jupyterhub/tags)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## Technical Overview
### Authenticators
We are using a custom multi authenticator to allow for multiple authentication methods. The following authenticators are used:

| Authenticator | Description |
| - | - |
| [Keycloak (Generic OAuth)](https://github.com/jupyterhub/oauthenticator/blob/main/oauthenticator/generic.py) | Login with SSO and standard account login |
| [LTI Authenticator](https://github.com/jupyterhub/ltiauthenticator) | Login with Moodle |

### Spawner (deprecated)
Each user is spawned in its own docker container. [Dockerspawner](https://github.com/jupyterhub/dockerspawner) is used to archieve this. A prespawn hook will be executed to set the displayed name of the user in e.g. a terminal. The CPU and memory is limited for each user.<br>
[Idleculler](https://github.com/jupyterhub/jupyterhub-idle-culler) is used to identify and shutdown idle or long-running Jupter Notebook servers.
A Juptyer Notebook server will always shutdown on logout.

## Installation
## Configuration

### Keycloak

### Environment Variables
|Variable|Value|
|-|-|
|||
|<b>OAuth</b>| |
| OAUTH2_TLS_VERIFY | 0 |
| OAUTH_CLIENT_ID | jupyterhub |
| OAUTH_CLIENT_SECRET | \<hidden> |
| OAUTH2_AUTHORIZE_URL | url to keycloak openid-connect auth |
| OAUTH2_INTERNAL_TOKEN_URL | url to keycloak openid-connect token internal (e.g. http://keycloak:8080/keycloak/realms/your_realm/protocol/openid-connect/token) |
| OAUTH_CALLBACK_URL | url to keycloak openid-connect callback |
| OAUTH2_INTERNAL_USERDATA_URL | url to keycloak openid-connect userinfo internal (e.g. http://keycloak:8080/keycloak/realms/your_realm/protocol/openid-connect/userinfo) |
|||
|<b>General</b>| |
| COMPOSE_PROJECT_NAME | jupyterhub |
| HOST | jupiter.fh-swf.de |
| JUPYTERHUB_CRYPT_KEY | \<hidden> |
| HUB_BASE_URL_PREFIX | /newhub |
| JUPYTERHUB_IMAGE | jupyterhub_testimg:latest |
| SPAWNER_CPU_LIMIT | 16 |
| SPAWNER_MEM_LIMIT | 40G |
|||
|<b>LTI</b>| |
| LTI_CLIENT_KEY | \<hidden> |
| LTI_SHARED_SECRET | \<hidden> |
|||
|<b>Deprecated</b>| |
| KEYCLOAK_LOGOUT_URL | \<deprecated> |
| LTI13_PRIVATE_KEY | \<deprecated> |
| OAUTH2_TOKEN_URL | url to keycloak openid-connect token \<deprecated> |
| OAUTH2_USERDATA_URL | url to keycloak openid-connect userinfo \<deprecated> |

To generate a random key, use the following command (linux):
> <command>openssl rand -base64 32</command>

### Moodle

To configure your moodle for lti authentication, see the official moodle documentations [\<here>](https://docs.moodle.org/400/de/LTI-Authentifizierung).

## Deployment

## Dockerimages
Jupyterhub deploys Jupyterlab instances as docker containers. With Docker Swarm (not swarm mode) you have to make sure that all nodes have the image already pulled as Jupyterhub currently does not pull them.
When logging in via Moodle LTI, i.e. via a link in a course, a course id gets transmitted. Jupyterhub will look for that id and search for available images with that id as a label, i.e.
```Dockerfile
    LABEL fhswf.jupyterhub.moodle.course.id="1234"
```
You can create a new Version of any image an give it a label with a single command:
```bash
    echo "FROM registry.io/image:tag | sudo docker build --label fhswf.jupyterhub.moodle.course.id="8161" -t "registry.io/image:moodlecourse-8161" -
```
The image has to present on all cluster nodes. So either run this command on all nodes or export and import the newly labeled image.

### Extend Images

To create new images based on the exsisting ones in this repo create a new Dockerfile and use the exsisting Image (for example ghcr.io/fhswf/jupyterhub/jupyterlab-scipy-gpu:main) as a base.

This Dockerfile would add open-ai gym to the exsisting torch notebook from this repo and assign it to moodle course id 8161:
```Dockerfile
FROM ghcr.io/fhswf/jupyterhub/jupyterlab-scipy-gpu:main

RUN pip install gym[all]

LABEL fhswf.jupyterhub.moodle.course.id="8161"
``` 
With the Dockerfile present in the current directory run:
```bash
sudo docker build . -t "myimage:moodlecourse-8161" 
```
Currently there is no automated pulling available, so this build needs to be repeated on every (gpu-)node in the cluster. 

## Contributing
## License (MIT)

Copyright (c) 2022 Fachhochschule Südwestfalen

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

**[Technical Overview](#technical-overview)** |
**[Installation](#installation)** |
**[Configuration](#configuration)** |
**[Deployment](#deployment)** |
**[Contributing](#contributing)** |
**[License](#license-mit)**
