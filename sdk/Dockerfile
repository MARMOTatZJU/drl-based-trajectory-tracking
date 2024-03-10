
FROM ubuntu:22.04
WORKDIR /

ENV DEBIAN_FRONTEND noninteractive

ARG USER_WORKDIR=/work_dir
ARG USER_BIN=/usr_bin
ARG USER_BASHRC=/work_dir/.bashrc

SHELL [ "/bin/bash", "-c" ]
ENV SHELL=/bin/bash

ARG APT_SOURCE_LIST=/etc/apt/sources.list
RUN \
    echo "Activating APT links to source code for in-container building" && \
    printf '\n' >> ${APT_SOURCE_LIST} && \
    printf "deb-src http://archive.ubuntu.com/ubuntu/ jammy main restricted universe multiverse" >> ${APT_SOURCE_LIST} && \
    printf '\n' >> ${APT_SOURCE_LIST} && \
    printf "deb-src http://archive.ubuntu.com/ubuntu/ jammy-updates main restricted universe multiverse" >> ${APT_SOURCE_LIST} && \
    printf '\n' >> ${APT_SOURCE_LIST} && \
    printf "deb-src http://archive.ubuntu.com/ubuntu/ jammy-security main restricted universe multiverse" >> ${APT_SOURCE_LIST} && \
    printf '\n' >> ${APT_SOURCE_LIST} && \
    printf "deb-src http://archive.ubuntu.com/ubuntu/ jammy-backports main restricted universe multiverse" >> ${APT_SOURCE_LIST} && \
    printf '\n' >> ${APT_SOURCE_LIST} && \
    apt update --fix-missing && \
    echo "Adding ppa:deadsnakes/ppa, for installing python3.x" && \
    DEBIAN_FRONTEND=noninteractive apt install -y software-properties-common && \
    add-apt-repository ppa:deadsnakes/ppa && \
    echo "Updating APT list" && \
    apt update --fix-missing && \
    echo "APT list configuration done."

RUN \
    echo "Installing network tools" && \
    apt install -y \
        ca-certificates \
        libssl-dev \
        curl wget \
        && \
    echo "Installing compiling tools" && \
    apt install -y \
        cmake \
        build-essential \
        cmake \
        python3 \
        && \
    echo "Installing system utilities" && \
    apt install -y \
        git \
        unzip \
        vim \
        && \
    echo "Fixing git openssl issue inside dockerfile building" && \
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
    echo "Configuring user's bashrc" && \
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
    unzip ${LIBTORCH_FILENAME} && \
    chmod -R 755 /libtorch

RUN \
    echo "Installing Python" && \
    echo "  Reference: https://github.com/ufoym/deepo/blob/master/docker/Dockerfile.pytorch-py38-cpu" && \
    echo "  Installing Python" && \
    PYTHON_VERSION=3.8 && \
    DEBIAN_FRONTEND=noninteractive apt install -y \
        python${PYTHON_VERSION} \
        python${PYTHON_VERSION}-dev \
        python${PYTHON_VERSION}-distutils \
        && \
    ln -s /usr/bin/python${PYTHON_VERSION} /usr/local/bin/python && \
    echo "Python installed."

RUN \
    echo "Installing pybind" && \
    echo "  Installing pip" && \
    wget https://bootstrap.pypa.io/get-pip.py && \
    python get-pip.py && \
    echo "  Installing pybind11" && \
    pip install pybind11[global] && \
    echo "pybind installed."


RUN \
    echo "Installing Doxygen..." && \
    DOXYGEN_VERSION=1.10.0 && \
    DOXYGEN_TARBALL_NAME=doxygen-${DOXYGEN_VERSION} && \
    DOXYGEN_TARBALL_FILENAME=${DOXYGEN_TARBALL_NAME}.linux.bin.tar.gz && \
    DOXYGEN_RELEASE_NAME=Release_$(echo $DOXYGEN_VERSION | sed -r 's/\./_/g') && \
    DOXYGEN_URL="https://github.com/doxygen/doxygen/releases/download/${DOXYGEN_RELEASE_NAME}/${DOXYGEN_TARBALL_FILENAME}" && \
    wget ${DOXYGEN_URL} && \
    tar -xzvf ${DOXYGEN_TARBALL_FILENAME} && \
        ( \
            cd ${DOXYGEN_TARBALL_NAME}; \
            cp -r ./bin/* /usr/local/bin/ ; \
        ) && \
    echo "Doxygen installed."
