/**
 * @file policy_inference.h
 * @brief Policy inference based on LibTorch.
 *
 */
#pragma once

#include <torch/script.h>
#include <torch/torch.h>
#include "common/io.h"

namespace drltt {

// TODO: logging
/**
 * @brief A policy based on torch JIT module.
 *
 */
class TorchJITModulePolicy {
 public:
  TorchJITModulePolicy() = default;
  ~TorchJITModulePolicy() {};
  /**
   * @brief Load a JIT module from a specified path.
   *
   * @param jit_module_path Path to JIT module.
   * @return true Module loading succeeded.
   * @return false Module loading failed.
   */
  bool load(const std::string& jit_module_path);
  /**
   * @brief Perform inference.
   *
   * @param observations_tensor The torch tensor of observations,
   * Shape={batch_size, observation_dim}.
   * @return torch::Tensor The torch tensor of actions. Shape={batch_size,
   * action_dim}
   */
  torch::Tensor infer(const torch::Tensor& observations_tensor);
  /**
   * @brief Perform inference.
   *
   * @param observations_vec Vector of observation data.
   * @param shape_vec Vector of the shape of observation tensor.
   * @return std::vector<float> , size=batch_size*action_dim
   */
  std::vector<float> infer(const std::vector<float>& observations_vec,
                           const std::initializer_list<int64_t>& shape_vec);
  /**
   * @brief Perform inference.
   *
   * @param observations_vec Vector of observation data. Assuming batch_size=1,
   * i.e. original shape={1, observation_dim}
   * @return std::vector<float> , size=batch_size*action_dim.
   */
  std::vector<float> infer(const std::vector<float>& observations_vec);

 protected:
  torch::jit::script::Module _module;
};
}  // namespace drltt
