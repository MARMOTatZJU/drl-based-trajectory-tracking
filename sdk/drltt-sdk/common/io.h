#pragma once

#include "drltt_proto/sdk/exported_policy_test_case.pb.h"
// #include "google/protobuf/descriptor.pb.h"
#include <torch/torch.h>
#include <vector>

namespace drltt {
// TODO: docstring
// TODO: use RVO and std::move to avoid copy
torch::Tensor parse_tensor_proto_to_torch_tensor(
    const drltt_proto::TensorFP& tensor_proto);
}  // namespace drltt
