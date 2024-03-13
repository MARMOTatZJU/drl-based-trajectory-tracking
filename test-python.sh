#!/bin/bash

source setup.sh

(
    echo "TEST PYTHON CODE"
    pytest
) 2>&1 | tee ./python-test.log
