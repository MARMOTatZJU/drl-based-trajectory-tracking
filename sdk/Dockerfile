
FROM ubuntu:22.04
WORKDIR /

ENV DEBIAN_FRONTEND noninteractive

ARG USER_WORKDIR=/work_dir

RUN \
    apt update && \
    apt install -y \
        cmake \
        build-essential \
        libblas-dev \
        liblapack-dev \
        libeigen3-dev \
        python3-opencv \
        libopencv-dev \
        libgtest-dev \
        libboost-all-dev \
        protobuf-compiler && \
    mkdir $USER_WORKDIR && chmod -R 777 $USER_WORKDIR
