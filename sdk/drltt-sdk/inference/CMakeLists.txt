project(drltt-sdk)
include_directories(${CMAKE_CURRENT_SOURCE_DIR})


file(GLOB_RECURSE _SRCS "*.[hc]pp")
list(FILTER _SRCS EXCLUDE REGEX "_test.[hc]pp$")
add_library(policy_inference STATIC ${_SRCS})
target_link_libraries(policy_inference
    ${Boost_FILESYSTEM_LIBRARY}
    ${Boost_SYSTEM_LIBRARY}
    ${TORCH_LIBRARIES}
    common
)

# gtest
file(GLOB_RECURSE _TEST_SRCS "*test.[hc]pp")
add_executable(
  policy_inference_test
  ${_TEST_SRCS}
)
target_link_libraries(
  policy_inference_test
  GTest::gtest_main
  policy_inference
  )
gtest_discover_tests(policy_inference_test)
