project(drltt-sdk)
include_directories(${CMAKE_CURRENT_SOURCE_DIR})

add_subdirectory(common)
add_subdirectory(dynamics_models)
add_subdirectory(inference)
add_subdirectory(managers)
add_subdirectory(environments)
add_subdirectory(trajectory_tracker)

# TODO: add another sample program
