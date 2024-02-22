cmake_minimum_required(VERSION 3.15)
project(drltt_sdk)

find_package(Protobuf REQUIRED)
include_directories(${PROTOBUF_INCLUDE_DIRS})

# compiled protobuf
include_directories(/work_dir/proto_gen_cpp)

add_subdirectory(drltt_sdk)
