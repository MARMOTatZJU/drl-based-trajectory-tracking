#!/bin/bash

echo "FORMATTING CPP CODE..."

if [[ ! -x $(command -v clang-format) ]];then
    echo "clang-format not found."
    exit -1
fi

clang_format_result=0
for f in $(find . -regex '.*\.\(cpp\|hpp\|cu\|cuh\|c\|h\)' \
    -not -path "./build/*" \
    -not -path "./proto_gen/*" \
    )
do
    clang-format --verbose --style=file --Werror ${CLANG_FORMAT_ARGS} -i $f
    if [ $? -ne 0 ]; then
        clang_format_result=$(($clang_format_result + 1))
    fi
done

exit ${clang_format_result}
