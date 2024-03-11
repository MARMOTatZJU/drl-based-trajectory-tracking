#!/bin/bash

set -exo pipefail

source ./install-setup-protoc.sh
source ./install-setup-doxygen.sh
source ./install-setup-protoc-gen-doc.sh

repo_dir=${PWD}
proto_dir=$(realpath common/proto)

bash ${proto_dir}/proto_def/compile_proto.sh

export PYTHONPATH=${repo_dir}:${PYTHONPATH}
export PYTHONPATH=:${proto_dir}/proto_gen_py:${PYTHONPATH}

echo "set PYTHONPATH: $PYTHONPATH"

set +exo pipefail
