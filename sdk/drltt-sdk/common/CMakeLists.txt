project(drltt_sdk)
include_directories(${CMAKE_CURRENT_SOURCE_DIR})
# TODO: reorg include paths, simplify them

file(GLOB_RECURSE _SRCS "*.[hc]pp")
list(FILTER _SRCS EXCLUDE REGEX "_test.[hc]pp$")
add_library(common STATIC ${_SRCS})
target_link_libraries(
    common
    ${PROTOBUF_LIBRARY}
    ${TORCH_LIBRARIES}
    proto
)

# gtest
if(BUILD_TESTS)
  file(GLOB_RECURSE _TEST_SRCS "*test.[hc]pp")
  add_executable(
    common_test
    ${_TEST_SRCS}
    )
    target_link_libraries(
      common_test
      GTest::gtest_main
      common
      )
    gtest_discover_tests(common_test)
endif(BUILD_TESTS)
