#!/bin/bash
src_dir=/proto_src

cpp_output_dir=/work_dir/proto_gen_cpp
rm -rf ${cpp_output_dir}
mkdir -p ${cpp_output_dir}

protoc -I ${src_dir} \
    --cpp_out ${cpp_output_dir} \
    --experimental_allow_proto3_optional \
    $(find ${src_dir} -name *.proto)
