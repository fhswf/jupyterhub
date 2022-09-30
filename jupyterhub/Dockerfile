FROM jupyterhub/jupyterhub:latest

ENV PYTHONUNBUFFERED=1

COPY . ./
COPY templates/images/logo.jpeg /usr/local/share/jupyter/hub/static/images/logo.jpeg

RUN pip install .

RUN pip install \
    oauthenticator \
    jupyterhub-ltiauthenticator \
    jupyterhub-idle-culler \
    dockerspawner \
    jupyterhub-traefik-proxy \
    nbgitpuller \
    MultiAuthenticator
