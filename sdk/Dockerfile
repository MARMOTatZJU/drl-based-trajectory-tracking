
FROM ubuntu:22.04
WORKDIR /

ENV DEBIAN_FRONTEND noninteractive

ARG USER_WORKDIR=/work_dir
ARG USER_BIN=/usr_bin
ARG USER_BASHRC=/work_dir/.bashrc

SHELL [ "/bin/bash", "-c" ]
ENV SHELL=/bin/bash

RUN apt update --fix-missing

RUN \
    echo "Installing compiling tools" && \
    apt install -y \
        cmake \
        build-essential \
        && \
    echo "Installing system utilities" && \
    apt install -y \
        curl wget \
        git \
        unzip \
        vim \
        && \
    echo "Fix git openssl issue inside dockerfile building" && \
        apt install -y gnutls-bin && \
        git config --global http.sslVerify false && \
        git config --global http.postBuffer 1048576000 && \
    echo "Installing dependency libraries" && \
    apt install -y \
        libblas-dev \
        liblapack-dev \
        libeigen3-dev \
        python3-opencv \
        libopencv-dev \
        libgtest-dev \
        libboost-all-dev \
        libabsl-dev \
        && \
    mkdir $USER_WORKDIR && chmod -R 777 $USER_WORKDIR && \
    mkdir $USER_BIN && chmod -R 777 $USER_BIN && \
    touch $USER_BASHRC && \
    echo "# Add LD_LIBRARY_PATH installed by user." >> $USER_BASHRC && \
    echo 'export LD_LIBRARY_PATH=/usr/local/lib:$LD_LIBRARY_PATH' >> $USER_BASHRC && \
    echo "source $USER_BASHRC" >> /root/.bashrc && \
    echo "apt package installation and bashrc modification done."

RUN \
    echo "Installing Protobuf" && \
    PROTO_VERSION=25.3 && \
    git clone --depth=1 --progress -b v${PROTO_VERSION} https://github.com/protocolbuffers/protobuf && \
        ( \
        cd protobuf; \
        git submodule update --depth=1 --init --recursive; \
        mkdir build; \
        cd build; \
        cmake ../ \
            -DCMAKE_BUILD_TYPE=Release \
            -Dprotobuf_BUILD_SHARED_LIBS=ON \
            -Dprotobuf_BUILD_TESTS=OFF; \
        make -j$(nproc --all) install; \
        ) && \
        rm -rf protobuf

RUN \
    echo "Installing gtest" && \
    GTEST_VERSION=1.14.0 && \
    git clone --depth=1 --progress -b v${GTEST_VERSION} https://github.com/google/googletest.git && \
        ( \
        cd googletest; \
        mkdir build; \
        cd build; \
        cmake ..; \
        make -j$(nproc --all) install; \
        ) && \
        rm -rf googletest

RUN \
    echo "Installing libtorch" && \
    LIBTORCH_VERSION=2.2.1 && \
    LIBTORCH_FILENAME="libtorch-cxx11-abi-shared-with-deps-${LIBTORCH_VERSION}+cpu.zip" && \
    LIBTORCH_FILENAME_IN_URL="libtorch-cxx11-abi-shared-with-deps-${LIBTORCH_VERSION}%2Bcpu.zip" && \
    LIBTORH_URL=https://download.pytorch.org/libtorch/cpu/${LIBTORCH_FILENAME_IN_URL} && \
    wget $LIBTORH_URL && \
    unzip ${LIBTORCH_FILENAME}
