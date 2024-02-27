#!/bin/bash

pushd build
    ld_lib_dir=$(realpath ./lib)
    export LD_LIBRARY_PATH=$ld_lib_dir:$LD_LIBRARY_PATH
    ./drltt-sdk/main
popd
