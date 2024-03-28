#!/bin/bash

log_dir=./test-log
mkdir -p $log_dir

(
    ./scripts/tests/train_eval_trace-track_test_sample.sh
    cd sdk
    export BUILD_DIR=$(realpath ./build)
    export PROTO_GEN_DIR=$(realpath ./proto_gen)
    export LIBTORCH_DIR=/libtorch
    export REPO_ROOT_DIR="$(git rev-parse --show-toplevel)"
    ./compile-source.sh
) 2>&1 | tee ./${log_dir}/cpp-test-ci.log
