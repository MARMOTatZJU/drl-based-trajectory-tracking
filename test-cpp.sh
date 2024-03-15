#!/bin/bash

log_dir=./test-log
mkdir -p $log_dir

source setup.sh 2>&1 | tee ./${log_dir}/cpp-test-setup.log

(
    echo "TEST CPP CODE"
    if [[ $1 == "fast"  ]]; then
        gen_data_script=./scripts/tests/train_eval_trace-track_test_sample_fast.sh
        shift
    else
        gen_data_script=./scripts/tests/train_eval_trace-track_test_sample.sh
    fi

    if [[ ! ( $1 == "test" && $2 == "reuse-checkpoint" ) ]]; then
        # generate checkpoint for sdk test
        $gen_data_script
    fi

    pushd sdk
        bash ./compile-in-docker.sh "$@"
    popd
) 2>&1 | tee ./${log_dir}/cpp-test.log
