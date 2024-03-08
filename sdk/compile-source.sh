#!/bin/bash

# NOTE: current directory is `./sdk/build`

# shared libraries
usr_lib_dir=/usr/local/lib
libtorch_lib_dir=/libtorch/lib
export LD_LIBRARY_PATH=$usr_lib_dir:$LD_LIBRARY_PATH

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
    cmake .. -DBUILD_TESTS=ON && make -j$(nproc --all) 2>&1 | tee ./build.log

    # export shared library.
    # TODO: consider a more elegant way, like packaging
    cp -r $usr_lib_dir ./
    cp -r ${libtorch_lib_dir} ./

    # print library size
    echo "User lib size: $(du -sh $usr_lib_dir)"
    echo "libtorch lib size: $(du -sh $libtorch_lib_dir)"

    ctest -VV --rerun-failed --output-on-failure 2>&1 | tee ./test.log

popd
