#!/bin/bash

./format-python-code.sh
python_check_result=$?

pushd ./sdk
    ./format-cpp-code.sh
    cpp_check_result=$?
popd

if [ $python_check_result -ne 0 ] || [ $cpp_check_result -ne 0 ]; then
    echo "Code formatting failed"
    exit 1
fi

echo "Code formatting succeeded"
exit 0
