#!/bin/bash

# shared libraries
ld_lib_dir=/usr/local/lib
export LD_LIBRARY_PATH=$ld_lib_dir:$LD_LIBRARY_PATH

# TODO figure out root cause and resolve it in more formal way
# https://stackoverflow.com/questions/19901934/libpthread-so-0-error-adding-symbols-dso-missing-from-command-line
export LDFLAGS="-Wl,--copy-dt-needed-entries"

# Check version and location of Protobuf compiler
echo "Using protoc $(protoc --version) at $(which protoc)"

rm -r ./build
mkdir -p ./build
pushd build
    cmake .. && make -j$(nproc --all)
    cp -r $ld_lib_dir ./    # export shared library.
                            # TODO: consider a more elegant way, like packaging
popd
