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


# RUN conda install -y -c conda-forge pytorch torchvision torchaudio cudatoolkit=${CUDAVERSION} cudnn=${CUDNNVERSION} -c pytorch -c nvidia
#RUN conda install pytorch torchvision torchaudio cudatoolkit=11.1 -c pytorch -c nvidia

# set up extra envs
ENV LD_LIBRARY_PATH=${CONDA_DIR}/lib/:${LD_LIBRARY_PATH}
RUN echo LD_LIBRARY_PATH="${LD_LIBRARY_PATH}" >> /etc/environment 
ENV CPATH=$CONDA_DIR/include
RUN echo CPATH="${CPATH}" >> /etc/environment

USER $NB_UID

# install torch with gpu support
RUN pip install torch==1.11.0+cu113 torchvision==0.12.0+cu113 torchaudio==0.12.0 --extra-index-url https://download.pytorch.org/whl/cu113

# install tensorflow/keras
#RUN pip install tensorflow 
RUN conda install -y -c conda-forge tensorflow-gpu cudatoolkit-dev cudnn

# RUN pip install -U jupyterhub
RUN pip install scilab-kernel 
