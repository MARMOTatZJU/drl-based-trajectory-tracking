#pragma once

#include "drltt_proto/sdk/exported_policy_test_case.pb.h"
#include "drltt_proto/dynamics_model/basics.pb.h"
#include <torch/torch.h>
#include <fstream>
#include <iostream>
#include <vector>

namespace drltt {

extern drltt_proto::DebugInfo global_debug_info;

// TODO: docstring
// TODO: use RVO and std::move to avoid copy
torch::Tensor parse_tensor_proto_to_torch_tensor(
    const drltt_proto::TensorFP& tensor_proto);

// TODO: docstring
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

// TODO: docstring
bool convert_tensor_to_vector(const torch::Tensor& tensor,
                              std::vector<float>* vector);

}  // namespace drltt
