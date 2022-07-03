FROM jupyterhub/jupyterhub:latest

ENV PYTHONUNBUFFERED=1

COPY . ./

RUN pip install .

RUN pip install \
    oauthenticator \
    jupyterhub-ltiauthenticator \
    jupyterhub-idle-culler \
    dockerspawner \
    jupyterhub-traefik-proxy \
    MultiAuthenticator

RUN mkdir -p /home/user/.ssh
COPY private.pem /home/user/.ssh/private.pem
COPY public.pem /home/user/.ssh/public.pem