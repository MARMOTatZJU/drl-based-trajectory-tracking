#!/bin/bash

# shared libraries
ld_lib_dir=/usr/local/lib
export LD_LIBRARY_PATH=$ld_lib_dir:$LD_LIBRARY_PATH

# TODO figure out root cause and resolve it in more formal way
# https://stackoverflow.com/questions/19901934/libpthread-so-0-error-adding-symbols-dso-missing-from-command-line
export LDFLAGS="-Wl,--copy-dt-needed-entries"

# Check version and location of Protobuf compiler
echo "Using protoc $(protoc --version) at $(which protoc)"

# Clear exisiting compiled files
rm -rf ./build
mkdir -p ./build
rm -rf ./proto_gen
mkdir -p ./proto_gen

# Configure and build
pushd build
    cmake .. && make -j$(nproc --all) 2>&1 | tee ./build.log
    cp -r $ld_lib_dir ./    # export shared library.
                            # TODO: consider a more elegant way, like packaging
    ctest -VV 2>&1 | tee ./test.log
popd
