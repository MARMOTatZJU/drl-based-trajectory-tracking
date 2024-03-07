project(drltt-sdk)
include_directories(${CMAKE_CURRENT_SOURCE_DIR})


file(GLOB_RECURSE _SRCS "*.[hc]pp")
list(FILTER _SRCS EXCLUDE REGEX "_test.[hc]pp$")
add_library(dynamics_models STATIC ${_SRCS})
target_link_libraries(dynamics_models
    ${Boost_FILESYSTEM_LIBRARY}
    ${Boost_SYSTEM_LIBRARY}
    ${PROTOBUF_LIBRARY}
    common
    proto
)

# gtest
if(BUILD_TESTS)
  file(GLOB_RECURSE _TEST_SRCS "*test.[hc]pp")
  add_executable(
    dynamics_models_test
    ${_TEST_SRCS}
  )
  target_link_libraries(
    dynamics_models_test
    GTest::gtest_main
    dynamics_models
    )
  gtest_discover_tests(dynamics_models_test)
endif(BUILD_TESTS)
