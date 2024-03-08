project(drltt-sdk)
include_directories(${CMAKE_CURRENT_SOURCE_DIR})


file(GLOB_RECURSE _SRCS "*.[hc]pp")
list(FILTER _SRCS EXCLUDE REGEX "_test.[hc]pp$")
add_library(inference STATIC ${_SRCS})
target_link_libraries(inference
    ${Boost_FILESYSTEM_LIBRARY}
    ${Boost_SYSTEM_LIBRARY}
    ${TORCH_LIBRARIES}
    common
)

# gtest
if(BUILD_TESTS)
  file(GLOB_RECURSE _TEST_SRCS "*test.[hc]pp")
  add_executable(
    inference_test
    ${_TEST_SRCS}
  )
  target_link_libraries(
    inference_test
    GTest::gtest_main
    inference
    )
  gtest_discover_tests(inference_test)
endif(BUILD_TESTS)
