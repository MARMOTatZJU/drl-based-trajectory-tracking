#!/bin/bash

work_dir=./test-log
if [[ -d $work_dir ]];then
    bak_work_dir=${work_dir}-bak
    if [[ -d ${bak_work_dir} ]];then rm -rf ${bak_work_dir};fi
    mv ${work_dir} ${bak_work_dir}
fi
mkdir -p $work_dir

test_script_dir=$(dirname $0)

./${test_script_dir}/test-python.sh "$@"
./${test_script_dir}/test-cpp.sh "$@"
./${test_script_dir}/test-doc.sh "$@"
