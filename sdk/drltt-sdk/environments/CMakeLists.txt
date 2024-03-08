project(drltt-sdk)
include_directories(${CMAKE_CURRENT_SOURCE_DIR})

file(GLOB_RECURSE _SRCS "*.[hc]pp")
list(FILTER _SRCS EXCLUDE REGEX "_test.[hc]pp$")
add_library(environments STATIC ${_SRCS})
target_link_libraries(environments
    common
    dynamics_models
    inference
    managers
    )

# gtest
if(BUILD_TESTS)
  file(GLOB_RECURSE _TEST_SRCS "*test.[hc]pp")
  add_executable(
    environments_test
    ${_TEST_SRCS}
  )
  target_link_libraries(
    environments_test
    environments
    GTest::gtest_main
    )
  gtest_discover_tests(environments_test)
endif(BUILD_TESTS)
