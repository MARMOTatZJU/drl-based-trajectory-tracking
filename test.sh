#!/bin/bash

source setup.sh

(
    echo "TEST PYTHON CODE"; \
    pytest; \
) 2>&1 | tee ./python-test.log


(
    echo "TEST CPP CODE"; \
    ./scripts/train_eval_trace-track_test_sample.sh
    pushd sdk; \
        bash ./compile-in-docker.sh; \
    popd; \
) 2>&1 | tee ./cpp-test.log
