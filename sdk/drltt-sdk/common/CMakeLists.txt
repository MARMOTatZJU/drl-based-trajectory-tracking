project(drltt_sdk)
include_directories(${CMAKE_CURRENT_SOURCE_DIR})

file(GLOB_RECURSE _SRCS "*.[hc]pp")
add_library(common STATIC ${_SRCS})
target_link_libraries(common
    ${Boost_FILESYSTEM_LIBRARY}
    ${Boost_SYSTEM_LIBRARY}
    ${PROTOBUF_LIBRARY}
)
