project(drltt-sdk)
include_directories(${CMAKE_CURRENT_SOURCE_DIR})

file(GLOB_RECURSE _SRCS "*.[hc]pp")
list(FILTER _SRCS EXCLUDE REGEX "_pybind_export.[hc]pp$")
add_library(trajectory_tracker STATIC ${_SRCS})
target_link_libraries(trajectory_tracker
    ${Boost_FILESYSTEM_LIBRARY}
    ${Boost_SYSTEM_LIBRARY}
    ${TORCH_LIBRARIES}
    environments
)

# pybind export
file(GLOB_RECURSE _EXPORT_SRCS "*_pybind_export.[hc]pp")
pybind11_add_module(
  trajectory_tracker_pybind_export
  ${_EXPORT_SRCS}
  )
target_include_directories(trajectory_tracker_pybind_export PRIVATE ${PYBIND11_INCLUDE_DIRS})
target_link_libraries(trajectory_tracker_pybind_export
  PRIVATE
  trajectory_tracker
)
