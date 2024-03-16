#!/bin/bash

set -exo pipefail
echo "DRLTT setup starts."

source ./setup-minimum.sh

source ./install-setup-protoc.sh
source ./install-setup-doxygen.sh
source ./install-setup-protoc-gen-doc.sh

# compile protobuf and generate documentation of protobuf
bash ${DRLTT_PROTO_DIR}/proto_def/compile_proto.sh

# generate documentation for cpp
(cd ./sdk ; doxygen Doxyfile-cpp)

echo "DRLTT setup finished."

set +exo pipefail
