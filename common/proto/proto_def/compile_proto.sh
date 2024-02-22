#!/bin/bash

echo "Start compiling protobuf."

src_dir=$(dirname $0)
python_output_dir=${src_dir}/../proto_gen_py/
rm -rf ${python_output_dir}
mkdir -p ${python_output_dir}
cpp_output_dir=${src_dir}/../proto_gen_cpp/
rm -rf ${cpp_output_dir}
mkdir -p ${cpp_output_dir}

# NOTE: if build cpp target within docker, protobuf also need to be compiled within docker.
#       otherwise, cpp compiler will not find protobuf include file.
# TODO: verify if `--experimental_allow_proto3_optional` is necessary
protoc -I ${src_dir} \
    --python_out ${python_output_dir} \
    --cpp_out ${cpp_output_dir} \
    --experimental_allow_proto3_optional \
    $(find ${src_dir} -name *.proto)

# create `__init__.py` files for compiled Python package
find ${python_output_dir} -mindepth 1 -type d -exec touch {}/__init__.py \;

echo "Protobuf compiled."
