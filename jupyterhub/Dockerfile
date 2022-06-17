FROM jupyterhub/jupyterhub:latest

COPY jupyterhub_config.py .

RUN pip install \
    jupyterhub-idle-culler \
    dockerspawner \
    jhub_cas_authenticator
