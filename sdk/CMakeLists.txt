cmake_minimum_required(VERSION 3.22)
project(drltt-sdk)
set(SDK_ROOT_DIR ${PROJECT_SOURCE_DIR})
include_directories(${CMAKE_CURRENT_SOURCE_DIR})

option(BUILD_TESTS "Build tests." OFF)
add_definitions(-DREPO_ROOT_DIR="$(git rev-parse --show-toplevel)")
add_definitions(-DMACRO_CHECKPOINT_DIR="${REPO_ROOT_DIR}/work_dir/track-test/checkpoint")
add_definitions(-DLIBTORCH_DIR="/libtorch")

message("Using checkpoint at ${MACRO_CHECKPOINT_DIR}.")

set(CMAKE_CXX_FLAGS "-O2 -Werror -fPIC -std=c++20 -march=native -ftree-vectorize")

# TODO resolve it in more formal way
# https://github.com/protocolbuffers/protobuf/issues/14500
# set(CMAKE_MODULE_LINKER_FLAGS "-Wl,--copy-dt-needed-entries")
# set(CMAKE_SHARED_LINKER_FLAGS "-Wl,--copy-dt-needed-entries")
# set(CMAKE_STATIC_LINKER_FLAGS "-Wl,--copy-dt-needed-entries")

# libtorch
set(LIBTORCH_CMAKE_PREFIX_PATH "${LIBTORCH_DIR}/share/cmake/")
list(APPEND CMAKE_PREFIX_PATH ${LIBTORCH_CMAKE_PREFIX_PATH})
find_package(Torch REQUIRED)
set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} ${TORCH_CXX_FLAGS}")
include_directories(SYSTEM ${TORCH_INCLUDE_DIRS})

# gtest
if(BUILD_TESTS)
    find_package(GTest REQUIRED)
    include_directories(${GTEST_INCLUDE_DIR})
    include(GoogleTest)
    enable_testing()
endif(BUILD_TESTS)

# protobuf
set(PROTO_GENERATE_PATH ${SDK_ROOT_DIR}/proto_gen)
add_subdirectory(${REPO_ROOT_DIR}/drltt/common/proto/proto_def proto_def)
include_directories(${PROTO_GENERATE_PATH})

# setup pybind11
execute_process(COMMAND "which python" OUTPUT_VARIABLE PYTHON_PATH)
set(PYTHON_EXECUTABLE ${PYTHON_PATH})
set(PYBIND11_FINDPYTHON ON)
find_package(pybind11 REQUIRED)
include_directories(${PYBIND11_INCLUDE_DIRS})


add_subdirectory(drltt-sdk)

