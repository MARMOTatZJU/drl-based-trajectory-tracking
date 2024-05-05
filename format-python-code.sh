#!/bin/bash

echo FORMATTING PYTHON CODE...

black ${BLACK_ARGS} --config ./configs/code_formatting/pyproject.toml ./
