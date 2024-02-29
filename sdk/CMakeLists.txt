cmake_minimum_required(VERSION 3.22)
project(drltt-sdk)
set(PROJECT_ROOT_PATH ${PROJECT_SOURCE_DIR})
include_directories(${CMAKE_CURRENT_SOURCE_DIR})

set(CMAKE_CXX_FLAGS "-fpic -Werror -O2 -std=c++20 -march=native -ftree-vectorize")

# TODO resolve it in more formal way
# https://github.com/protocolbuffers/protobuf/issues/14500
# set(CMAKE_MODULE_LINKER_FLAGS "-Wl,--copy-dt-needed-entries")
# set(CMAKE_SHARED_LINKER_FLAGS "-Wl,--copy-dt-needed-entries")
# set(CMAKE_STATIC_LINKER_FLAGS "-Wl,--copy-dt-needed-entries")

find_package(Boost REQUIRED)
include_directories(${Boost_INCLUDE_DIRS})

# gtest
find_package(GTest REQUIRED)
include_directories(${GTEST_INCLUDE_DIR})
include(GoogleTest)
enable_testing()

add_subdirectory(/proto/proto_def proto_def)
include_directories(/drltt-sdk/proto_gen)  # TODO resolve it in more formal way, try to find a nother place in sdk folder


add_subdirectory(drltt-sdk)

