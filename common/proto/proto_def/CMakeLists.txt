find_package(Protobuf REQUIRED)
include_directories(${PROTOBUF_INCLUDE_DIRS})

# TODO remove redundant set of this part
set(PROTOBUF_GENERATE_CPP_APPEND_PATH FALSE)
set(PROTOBUF_IMPORT_DIRS ${CMAKE_CURRENT_SOURCE_DIR} PROTOC_OUT_DIR ${PROTO_GENERATE_PATH})
file(GLOB_RECURSE PROTO_DEF "${CMAKE_CURRENT_SOURCE_DIR}/*.proto")
protobuf_generate_cpp(PROTO_SRC PROTO_HEADER ${PROTO_DEF} )

# compile protobuf-generated source
include_directories(${PROTO_GENERATE_PATH})
add_library(proto STATIC ${PROTO_HEADER} ${PROTO_SRC})
target_link_libraries(proto PRIVATE ${Protobuf_LIBRARIES})
