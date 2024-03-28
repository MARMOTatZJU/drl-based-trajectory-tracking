#!/bin/bash

log_dir=./test-log
mkdir -p $log_dir


(

    echo "SETTING UP CPP TESTING ENVIRONMENT"
    if [[ $1 == "fast"  ]]; then
        gen_data_script=./scripts/tests/train_eval_trace-track_test_sample_fast.sh
        shift
    else
        gen_data_script=./scripts/tests/train_eval_trace-track_test_sample.sh
    fi

    if [[ ! ( $1 == "test" && $2 == "reuse-checkpoint" ) ]]; then
        # generate checkpoint for sdk test
        source $gen_data_script
    else
        source setup.sh
    fi
    echo "TEST CPP CODE"
    pushd sdk
        bash ./compile-in-docker.sh "$@"
    popd
) 2>&1 | tee ./${log_dir}/cpp-test.log
