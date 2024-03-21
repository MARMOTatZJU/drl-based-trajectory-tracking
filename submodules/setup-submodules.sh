#!/bin/bash

drltt_proto_gen_py_dir_default="${DRLTT_REPO_DIR}/submodules/drltt-assets/proto_gen_py/"
export PYTHONPATH=:${drltt_proto_gen_py_dir_default}:${PYTHONPATH}

waymax_viz_dir=submodules/waymax-visualization
export PYTHONPATH=:${waymax_viz_dir}:${PYTHONPATH}

