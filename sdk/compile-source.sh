#!/bin/bash

mkdir -p ./build
pushd build
    cmake .. && make -j2
popd
