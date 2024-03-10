#!/bin/bash

# - release v21.12, 2022/12/14
#   - https://github.com/protocolbuffers/protobuf/releases/tag/v21.12
# - tag v3.21.12, 2022/12/13
#     - https://github.com/protocolbuffers/protobuf/releases/tag/v3.21.12
# - installation instruction
#   - https://google.github.io/proto-lens/installing-protoc.html

protobuf_release_version="21.12"
proto_release_filename=protoc-${protobuf_release_version}-linux-x86_64.zip

home_bin_dir=$HOME/.local/bin
export PATH=${home_bin_dir}:$PATH

if [[ ! -x $(command -v protoc) ]];then
  mkdir -p ${home_bin_dir}
  protoc_binary=${home_bin_dir}/protoc
  if [[ ! -f ${protoc_binary} ]];then
    tmp_dir=/tmp/drltt-$(openssl rand -hex 6)
    mkdir ${tmp_dir}
    pushd ${tmp_dir}
      curl -OL https://github.com/protocolbuffers/protobuf/releases/download/v${protobuf_release_version}/${proto_release_filename}
      unzip ${proto_release_filename} -d protobuf-release/
      mv protobuf-release/bin/protoc ${home_bin_dir}
    popd
    rm -rf ${tmp_dir}
  fi
fi

echo "protoc installed and setup at $(which protoc)"
