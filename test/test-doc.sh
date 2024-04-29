#!/bin/bash

log_dir=./test-log
mkdir -p $log_dir

(
    source setup.sh
    ./docs/make-html.sh
    retval=$?
) 2>&1 | tee ./${log_dir}/doc-test.log

exit $retval
