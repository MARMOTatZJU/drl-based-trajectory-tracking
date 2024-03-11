#!/bin/bash

set -exo pipefail
echo "DRLTT setup starts."

source ./install-setup-protoc.sh
source ./install-setup-doxygen.sh
source ./install-setup-protoc-gen-doc.sh

repo_dir=${PWD}
proto_dir=$(realpath common/proto)

# compile protobuf and generate documentation of protobuf
bash ${proto_dir}/proto_def/compile_proto.sh

# generate documentation for cpp
(cd ./sdk ; doxygen Doxyfile-cpp)

export PYTHONPATH=${repo_dir}:${PYTHONPATH}
export PYTHONPATH=:${proto_dir}/proto_gen_py:${PYTHONPATH}

echo "set PYTHONPATH: $PYTHONPATH"

echo "DRLTT setup finished."

set +exo pipefail
