#!/bin/bash

# NOTE: current directory is `./sdk/build`

# shared libraries
export LD_LIBRARY_PATH=$LD_LIBRARY_PATH:$USR_LIB_DIR

# TODO figure out root cause and resolve it in more formal way
# https://stackoverflow.com/questions/19901934/libpthread-so-0-error-adding-symbols-dso-missing-from-command-line
export LDFLAGS="-Wl,--copy-dt-needed-entries"

# Check version and location of Protobuf compiler
echo "Using protoc $(protoc --version) at $(which protoc)"

# Clear exisiting compiled files
rm -rf ${BUILD_DIR}
mkdir -p ${BUILD_DIR}
rm -rf ${PROTO_GEN_DIR}
mkdir -p ${PROTO_GEN_DIR}

# Configure and build
pushd ${BUILD_DIR}
    cmake .. \
        -DBUILD_TESTS=ON \
        -DMACRO_CHECKPOINT_DIR=${CHECKPOINT_DIR} \
        -DLIBTORCH_DIR=${LIBTORCH_DIR} \
        && make -j$(nproc --all) 2>&1 | tee ./build.log
    ctest -VV --rerun-failed --output-on-failure 2>&1 | tee ./test.log
popd
