#include "policy_inference.h"

namespace drltt {

void TorchJITModulePolicy::load(const std::string& jit_module_path) {
  _module = torch::jit::load(jit_module_path);
}

torch::Tensor TorchJITModulePolicy::infer(
    const torch::Tensor& observations_tensor) {
  // TODO: use RVO and std::move to reduce copy
  std::vector<torch::jit::IValue> jit_inputs;
  jit_inputs.push_back(observations_tensor);
  torch::Tensor jit_actions_tensor = _module.forward(jit_inputs).toTensor();

  return jit_actions_tensor;
}

}  // namespace drltt
