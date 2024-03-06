#include "policy_inference.h"

namespace drltt {

bool TorchJITModulePolicy::load(const std::string& jit_module_path) {
  _module = torch::jit::load(jit_module_path);
  return true;
}

torch::Tensor TorchJITModulePolicy::infer(
    const torch::Tensor& observations_tensor) {
  // TODO: use RVO and std::move to reduce copy
  std::vector<torch::jit::IValue> jit_inputs;
  jit_inputs.push_back(observations_tensor);
  torch::Tensor jit_actions_tensor = _module.forward(jit_inputs).toTensor();

  return jit_actions_tensor;
}

// TODO: use RVO and std::move to reduce copy
std::vector<float> TorchJITModulePolicy::infer(
    const std::vector<float>& observations_vec,
    const std::initializer_list<int64_t>& shape_vec) {
  std::vector<float> observations_vec_copied(observations_vec.begin(),
                                             observations_vec.end());
  torch::Tensor observation_tensor =
      torch::from_blob(observations_vec_copied.data(), shape_vec,
                       torch::kFloat32)
          .view(shape_vec);
  torch::Tensor jit_actions_tensor = infer(observation_tensor);
  std::vector<float> actions_vec;
  convert_tensor_to_vector(jit_actions_tensor, &actions_vec);
  return actions_vec;
}

// TODO: use RVO and std::move to reduce copy
std::vector<float> TorchJITModulePolicy::infer(
    const std::vector<float>& observations_vec) {
  return infer(observations_vec,
               {1, static_cast<int64_t>(observations_vec.size())});
}

}  // namespace drltt
