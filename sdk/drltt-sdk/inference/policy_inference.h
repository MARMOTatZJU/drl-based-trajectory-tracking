#pragma once

#include <torch/script.h>
#include <torch/torch.h>
#include "common/io.h"

namespace drltt {

// TODO: docstring
// TODO: logging
class TorchJITModulePolicy {
 public:
  TorchJITModulePolicy() = default;
  ~TorchJITModulePolicy() {};
  bool load(const std::string& jit_module_path);
  torch::Tensor infer(const torch::Tensor& observations_tensor);
  std::vector<float> infer(const std::vector<float>& observations_vec,
                           const std::initializer_list<int64_t>& shape_vec);
  std::vector<float> infer(const std::vector<float>& observations_vec);

 protected:
  torch::jit::script::Module _module;
};
}  // namespace drltt
