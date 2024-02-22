project(drltt_sdk)
include_directories(${CMAKE_CURRENT_SOURCE_DIR})

add_executable(main main.cpp)
target_link_directories(main PRIVATE /proto_gen_cpp)
