ARG CUDAVERSION=11.7
ARG CUDNNVERSION=8.1.0

FROM ghcr.io/fhswf/jupyterhub-docker-stacks/scipy-notebook:latest
#FROM jupyter/scipy-notebook:latest

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
    htop \
    wget \
    iputils-ping \
    && apt-get clean && \
    rm -rf /var/lib/apt/lists/*

USER $NB_UID

RUN pip install jupyterhub scilab-kernel \
    pip  install torch torchvision torchaudio --extra-index-url https://download.pytorch.org/whl/cu116

USER root

ENV LD_LIBRARY_PATH=${CONDA_DIR}/lib/:${LD_LIBRARY_PATH}
RUN echo LD_LIBRARY_PATH="${LD_LIBRARY_PATH}" >> /etc/environment 
ENV CPATH=$CONDA_DIR/include
RUN echo CPATH="${CPATH}" >> /etc/environment

USER $NB_UID

ENV CPATH=$CONDA_DIR/include:$CPATH

# the label fhswf.jupyterhub.runtime has to be present for runtime detection of available images 
LABEL fhswf.jupyterhub.runtime="NVIDIA-GPU"
LABEL fhswf.jupyterhub.moodle.course.id="8161"
