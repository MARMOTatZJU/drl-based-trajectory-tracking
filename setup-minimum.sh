#!/bin/bash
# THIS SCRIPT NEEDS TO BE RUN AT THE ROOT DIR. OF THE REPO.

export DRLTT_REPO_DIR=${PWD}
export DRLTT_PROTO_DIR=$(realpath common/proto)
export DRLTT_PROTO_GEN_PY_DIR=${DRLTT_PROTO_DIR}/proto_gen_py

source submodules/setup-submodules.sh

export PYTHONPATH=${DRLTT_REPO_DIR}:${PYTHONPATH}
export PYTHONPATH=:${DRLTT_PROTO_GEN_PY_DIR}:${PYTHONPATH}

echo "set PYTHONPATH: $PYTHONPATH"
