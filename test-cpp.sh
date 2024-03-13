#!/bin/bash

source setup.sh

(
    echo "TEST CPP CODE"
    if [[ ! ( $1 == "test" && $2 == "reuse-checkpoint" ) ]]; then
        ./scripts/train_eval_trace-track_test_sample.sh  # generate checkpoint for sdk test
    fi

    pushd sdk
        bash ./compile-in-docker.sh $@
    popd
) 2>&1 | tee ./cpp-test.log
