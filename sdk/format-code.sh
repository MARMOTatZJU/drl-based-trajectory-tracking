#!/bin/bash

echo "FORMATTING CPP CODE..."
find . -regex '.*\.\(cpp\|hpp\|cu\|cuh\|c\|h\)' -not -path "./build/*" -exec clang-format --verbose --style=file -i {} \;