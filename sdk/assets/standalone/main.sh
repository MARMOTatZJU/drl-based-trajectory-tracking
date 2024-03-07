#!/bin/bash

pip install -r ./requirements.txt

export LD_LIBRARY_PATH=./lib:${LD_LIBRARY_PATH}
export PYTHONPATH=$PWD:$PYTHONPATH
export PYTHONPATH=./proto_gen_py:$PYTHONPATH

python test_export_symbols.py
