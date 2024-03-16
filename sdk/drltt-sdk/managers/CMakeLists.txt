project(drltt-sdk)
include_directories(${CMAKE_CURRENT_SOURCE_DIR})


file(GLOB_RECURSE _SRCS "*.[hc]pp")
list(FILTER _SRCS EXCLUDE REGEX "_test.[hc]pp$")
add_library(managers STATIC ${_SRCS})
target_link_libraries(managers
    ${TORCH_LIBRARIES}
    common
    dynamics_models
)

