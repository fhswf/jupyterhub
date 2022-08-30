ARG CUDAVERSION=11.7
ARG CUDNNVERSION=8.1.0

#FROM ghcr.io/fhswf/jupyterhub-docker-stacks/scipy-notebook:latest
FROM jupyter/scipy-notebook:latest

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

RUN conda install -y -c conda-forge cudatoolkit=${CUDAVERSION} cudnn=${CUDNNVERSION}

USER root

ENV LD_LIBRARY_PATH=${CONDA_DIR}/lib/:${LD_LIBRARY_PATH}
RUN echo LD_LIBRARY_PATH="${LD_LIBRARY_PATH}" >> /etc/environment 

USER $NB_UID

RUN pip install \
    # pycuda \
    tensorflow \
    torch \
    torchvision \
    torchaudio 
    #--extra-index-url https://download.pytorch.org/whl/cu102

ENV CPATH=$CONDA_DIR/include

RUN pip install \
    scilab-kernel 
