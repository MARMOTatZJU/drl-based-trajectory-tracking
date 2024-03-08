#!/bin/bash

pip install -r ./requirements.txt

export LD_LIBRARY_PATH=./lib:${LD_LIBRARY_PATH}
export PYTHONPATH=$PWD:$PYTHONPATH
export PYTHONPATH=./proto_gen_py:$PYTHONPATH

python ./check_export_symbols.py
