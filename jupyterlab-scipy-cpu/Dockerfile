FROM jupyter/scipy-notebook:latest

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
    tensorflow \
    torch \
    torchvision \
    torchaudio \
    --extra-index-url https://download.pytorch.org/whl/cpu

ENV CPATH=$CONDA_DIR/include

RUN pip install \
    scilab-kernel 
    
# the label fhswf.jupyterhub.runtime has to be present for runtime detection of available images 
LABEL fhswf.jupyterhub.runtime="CPU"
LABEL fhswf.jupyterhub.moodle.course.id="8161"
