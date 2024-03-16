#!/bin/bash

log_dir=./test-log
mkdir -p $log_dir

(
    echo "SETTING UP PYTHON TESTING ENVIRONMENT"
    source setup.sh
    echo "TEST PYTHON CODE"
    pytest
) 2>&1 | tee ./${log_dir}/python-test.log
