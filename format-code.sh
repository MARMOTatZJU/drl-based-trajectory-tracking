#!/bin/bash

echo FORMATTING PYTHON CODE...
black --config ./configs/code_formatting/pyproject.toml ./

pushd ./sdk
    bash ./format-code.sh
popd
