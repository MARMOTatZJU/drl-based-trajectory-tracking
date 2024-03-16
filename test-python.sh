#!/bin/bash

log_dir=./test-log
mkdir -p $log_dir

(
    echo "SETTING UP PYTHON TESTING ENVIRONMENT"
    source setup.sh
    ./scripts/tests/train_eval_trace-track_test_sample_dummy.sh
    echo "TEST PYTHON CODE"
    pytest
) 2>&1 | tee ./${log_dir}/python-test.log
