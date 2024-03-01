#!/bin/bash

source setup.sh

(
    echo "TEST PYTHON CODE"; \
    pytest; \
) 2>&1 | tee ./python-test.log


(
    echo "TEST CPP CODE"; \
    pushd sdk; \
        bash ./compile-in-docker.sh; \
    popd; \
) 2>&1 | tee ./cpp-test.log
