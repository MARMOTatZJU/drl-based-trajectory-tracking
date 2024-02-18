#!/bin/bash
set -eo pipefail

repo_dir=${PWD}
proto_dir=$(realpath common/proto)

bash ${proto_dir}/proto_def/compile_proto.sh

export PYTHONPATH=${repo_dir}:${PYTHONPATH}
export PYTHONPATH=:${proto_dir}/proto_gen_py:${PYTHONPATH}

echo "set PYTHONPATH: $PYTHONPATH"

set +eo pipefail
