#!/bin/bash
source setup.sh
work_dir=work_dirs/tiny-track
if [[ -d $work_dir ]];then
    mv $work_dir $work_dir-bak
fi
mkdir -p $work_dir

python tools/main.py \
    --config-files \
        configs/trajectory_tracking/config-track-base.yaml \
        configs/trajectory_tracking/config-track-tiny.yaml \
    --checkpoint-dir $work_dir/checkpoint \
    --train --eval
