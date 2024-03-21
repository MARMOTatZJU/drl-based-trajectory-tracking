#pragma once

#include <torch/torch.h>
#include <fstream>
#include <iostream>
#include <vector>
#include "drltt_proto/dynamics_model/basics.pb.h"
#include "drltt_proto/sdk/exported_policy_test_case.pb.h"

namespace drltt {

extern drltt_proto::DebugInfo global_debug_info;

/**
 * @brief Parse tensor in proto to torch Tensor.
 *    TODO: use RVO and std::move to avoid copy
 *
 * @param tensor_proto Tensor in proto.
 * @return torch::Tensor Parsed torch Tensor.
 */
torch::Tensor parse_tensor_proto_to_torch_tensor(
    const drltt_proto::TensorFP& tensor_proto);

/**
 * @brief Parse protobuf message from binary file.
 *
 * @tparam T The type of protobuf message.
 * @param proto_msg Protobuf message.
 * @param proto_path Path to the binary file.
 * @return true Parsing succeeded.
 * @return false Parsing failed.
 */
template <typename T>
bool parse_proto_from_file(T& proto_msg, const std::string& proto_path) {
  std::fstream input(proto_path, std::ios::in | std::ios::binary);
  if (!input) {
    std::cerr << proto_path << " not found!!!" << std::endl;
    return false;
  } else if (!proto_msg.ParseFromIstream(&input)) {
    std::cerr << "Parsing error." << std::endl;
    return false;
  }
  input.close();
  return true;
}

/**
 * @brief Convert tensor to std::vector.
 *
 * @param tensor Source tensor.
 * @param vector Vector to store converted data.
 * @return true Conversion succeeded.
 * @return false Conversion failed.
 */
bool convert_tensor_to_vector(const torch::Tensor& tensor,
                              std::vector<float>* vector);

}  // namespace drltt
