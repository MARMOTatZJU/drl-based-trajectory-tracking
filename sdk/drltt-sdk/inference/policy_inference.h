#pragma once

#include <torch/script.h>
#include <torch/torch.h>

namespace drltt {

// TODO: docstring
// TODO: logging
class TorchJITModulePolicy {
 public:
  TorchJITModulePolicy() = default;
  void load(const std::string& jit_module_path);
  torch::Tensor infer(const torch::Tensor& observations_tensor);

 protected:
  torch::jit::script::Module _module;
};
}  // namespace drltt
