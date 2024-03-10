#!/bin/bash

DOXYGEN_VERSION="1.10.0"

home_bin_dir=$HOME/.local/bin
export PATH=${home_bin_dir}:$PATH

if [[ ! -x $(command -v doxygen) ]];then
  mkdir -p ${home_bin_dir}
  doxygen_binary=${home_bin_dir}/doxygen
  if [[ ! -f ${doxygen_binary} ]];then
    tmp_dir=/tmp/drltt-$(openssl rand -hex 6)
    mkdir ${tmp_dir}
    pushd ${tmp_dir}
      DOXYGEN_TARBALL_NAME=doxygen-${DOXYGEN_VERSION}
      DOXYGEN_TARBALL_FILENAME=${DOXYGEN_TARBALL_NAME}.linux.bin.tar.gz
      DOXYGEN_RELEASE_NAME=Release_$(echo $DOXYGEN_VERSION | sed -r 's/\./_/g')
      DOXYGEN_URL="https://github.com/doxygen/doxygen/releases/download/${DOXYGEN_RELEASE_NAME}/${DOXYGEN_TARBALL_FILENAME}"
      curl -OL ${DOXYGEN_URL}
      tar -xzvf ${DOXYGEN_TARBALL_FILENAME} && \
          ( \
              cd ${DOXYGEN_TARBALL_NAME}; \
              mv ./bin/* $home_bin_dir/ ; \
          )
    popd
    rm -rf ${tmp_dir}
  fi
fi
