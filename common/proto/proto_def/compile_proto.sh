#!/bin/bash
src_dir=$(dirname $0)
python_output_dir=${src_dir}/../proto_gen_py/
rm -rf ${python_output_dir}
mkdir -p ${python_output_dir}
cpp_output_dir=${src_dir}/../proto_gen_cpp/
rm -rf ${cpp_output_dir}
mkdir -p ${cpp_output_dir}

protoc -I ${src_dir} \
    --python_out ${python_output_dir} \
    --cpp_out ${cpp_output_dir} \
    ${src_dir}/**/*.proto

# create `__init__.py` files for compiled Python package
find ${python_output_dir} -type d -exec touch {}/__init__.py \;
echo "Proto compiled."
