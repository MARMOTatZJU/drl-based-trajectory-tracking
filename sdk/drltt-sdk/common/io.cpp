#include "io.h"

namespace drltt {
torch::Tensor parse_tensor_proto_to_torch_tensor(
    const drltt_proto::TensorFP& tensor_proto) {
  std::vector<int64_t> shape_vec(tensor_proto.shape().begin(),
                                 tensor_proto.shape().end());
  // TODO: verify type
  std::vector<float> data_vec(tensor_proto.data().begin(),
                              tensor_proto.data().end());

  // TODO: remove copy by using RVO and std::move
  // NOTE: only data_vec.data() pointer copied. data need to be copied
  // otherwise.
  torch::Tensor parsed_tensor =
      torch::from_blob(data_vec.data(), shape_vec, torch::kFloat32);

  // TODO: remove copy by using RVO and std::move
  return parsed_tensor.clone();
}
}  // namespace drltt
