FROM ghcr.io/fhswf/jupyterhub-docker-stacks/scipy-notebook:latest

# some alternative route is here: https://github.com/iot-salzburg/gpu-jupyter
# not sure if this version is better then what we have now

LABEL maintainer="FH SWF"

USER root

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    fonts-dejavu \
    tzdata \
    gfortran \
    gcc \
    scilab \
    pari-gp \
    libpari-dev \
    libgmp-dev \
    && apt-get clean && \
    rm -rf /var/lib/apt/lists/*

USER $NB_UID

RUN pip install -U jupyterhub

RUN pip install \
    # pycuda \
    tensorflow-gpu \
    torch \
    torchvision \
    torchaudio 
    #--extra-index-url https://download.pytorch.org/whl/cu102

ENV CPATH=$CONDA_DIR/include

RUN pip install \
    scilab-kernel 
