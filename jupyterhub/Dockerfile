FROM jupyterhub/jupyterhub:2.3.1

RUN pip install -U jupyterhub==2.3.1

RUN jupyterhub upgrade-db

COPY jupyterhub_config.py .

RUN pip install \
    jupyterhub-idle-culler \
    dockerspawner \
    jhub_cas_authenticator
