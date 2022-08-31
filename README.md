**[Technical Overview](#technical-overview)** |
**[Installation](#installation)** |
**[Configuration](#configuration)** |
**[Contributing](#contributing)** |
**[License](#license)**

# [Spawn Jupyterhub in dockercontainer](https://github.com/fhswf/jupyterhub)

[![Docker Image CI](https://github.com/fhswf/jupyterhub/actions/workflows/docker-image-ci.yml/badge.svg?branch=main)](https://github.com/fhswf/jupyterhub/actions/workflows/docker-image-ci.yml)
[![GitHub](https://img.shields.io/badge/issue_tracking-github-blue?logo=github)](https://github.com/fhswf/jupyterhub/issues)
[![GitHub Tags](https://img.shields.io/github/v/tag/fhswf/jupyterhub?style=plastic)](https://github.com/fhswf/jupyterhub/tags)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Documentation Status](https://readthedocs.org/projects/jupyterhub-test-dokumentation/badge/?version=latest)](https://jupyterhub-test-dokumentation.readthedocs.io/en/latest/?badge=latest)

## Technical Overview
### Authenticators
We are using a custom multi authenticator to allow for multiple authentication methods. The following authenticators are used:

| Authenticator | Description |
| - | - |
| [Keycloak (Generic OAuth)](https://github.com/jupyterhub/oauthenticator/blob/main/oauthenticator/generic.py) | Login with SSO and standard account login |
| [LTI Authenticator](https://github.com/jupyterhub/ltiauthenticator) | Login with Moodle |

### Spawner
Each user is spawned in its own docker container. [Dockerspawner](https://github.com/jupyterhub/dockerspawner) is used to archieve this. A prespawn hook will be executed to set the displayed name of the user in e.g. a terminal. The CPU and memory is limited for each user.<br>
[Idleculler](https://github.com/jupyterhub/jupyterhub-idle-culler) is used to identify and shutdown idle or long-running Jupter Notebook servers.
A Juptyer Notebook server will always shutdown on logout.

## Installation
## Configuration
## Contributing
## License
