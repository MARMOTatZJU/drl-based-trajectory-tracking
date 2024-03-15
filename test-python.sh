#!/bin/bash

log_dir=./test-log
mkdir -p $log_dir

source setup.sh 2>&1 | tee ./${log_dir}/python-test-setup.log

(
    echo "TEST PYTHON CODE"
    pytest
) 2>&1 | tee ./${log_dir}/python-test.log
