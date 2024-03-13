#!/bin/bash
source setup.sh
work_dir=work_dir/track
if [[ -d $work_dir ]];then
    bak_work_dir=${work_dir}-bak
    if [[ -d ${bak_work_dir} ]];then rm -rf ${bak_work_dir};fi
    mv ${work_dir} ${bak_work_dir}
fi
mkdir -p $work_dir

script_path=$0
cp $script_path $work_dir/

python tools/main.py \
    --config-files \
        configs/trajectory_tracking/config-track-base.yaml \
        configs/trajectory_tracking/config-track.yaml \
    --checkpoint-dir $work_dir/checkpoint \
    --num-test-cases 1024 \
    --train --eval --trace
