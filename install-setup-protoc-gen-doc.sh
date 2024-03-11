#!/bin/bash

PROTO_GEN_DOC_VERSION="1.5.1"

home_bin_dir=$HOME/.local/bin
export PATH=${home_bin_dir}:$PATH

if [[ ! -x $(command -v protoc-gen-doc) ]];then
  mkdir -p ${home_bin_dir}
  protoc_doc_gen_binary=${home_bin_dir}/protoc-gen-doc
  if [[ ! -f ${protoc_doc_gen_binary} ]];then
    tmp_dir=/tmp/drltt-$(openssl rand -hex 6)
    mkdir ${tmp_dir}
    pushd ${tmp_dir}
      PROTO_GEN_DOC_FILENAME=protoc-gen-doc_${PROTO_GEN_DOC_VERSION}_linux_amd64.tar.gz && \
      curl -OL https://github.com/pseudomuto/protoc-gen-doc/releases/download/v${PROTO_GEN_DOC_VERSION}/${PROTO_GEN_DOC_FILENAME} && \
      tar -xvf ${PROTO_GEN_DOC_FILENAME} -C $home_bin_dir/ protoc-gen-doc && \
    popd
    rm -rf ${tmp_dir}
  fi
fi
