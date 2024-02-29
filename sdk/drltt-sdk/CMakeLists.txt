project(drltt-sdk)
include_directories(${CMAKE_CURRENT_SOURCE_DIR})

add_subdirectory(common)
add_subdirectory(dynamics_models)

add_executable(main main.cpp)
# TODO remove redundant linked libraries
target_link_libraries(main PRIVATE 
    ${Protobuf_LIBRARIES}
    ${Boost_FILESYSTEM_LIBRARY}
    ${Boost_SYSTEM_LIBRARY}
    ${PROTOBUF_LIBRARY}
    proto
    common
)

