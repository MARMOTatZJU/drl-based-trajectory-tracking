project(drltt-sdk)
include_directories(${CMAKE_CURRENT_SOURCE_DIR})


file(GLOB_RECURSE _SRCS "*.[hc]pp")
list(FILTER _SRCS EXCLUDE REGEX "_test.[hc]pp$")
add_library(dynamics_model STATIC ${_SRCS})
target_link_libraries(dynamics_model
    ${Boost_FILESYSTEM_LIBRARY}
    ${Boost_SYSTEM_LIBRARY}
    ${PROTOBUF_LIBRARY}
)
