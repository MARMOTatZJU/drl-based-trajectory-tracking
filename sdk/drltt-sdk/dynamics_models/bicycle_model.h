#pragma once

#include <cmath>
#include "base_dynamics_model.h"
#include "common/protobuf_operators.h"
#include "drltt-sdk/common/geometry.h"

namespace drltt {

class BicycleModel : public BaseDynamicsModel {
 public:
  BicycleModel() = default;
  BicycleModel(const drltt_proto::HyperParameter& hyper_parameter)
      : BaseDynamicsModel(hyper_parameter) {}
  BicycleModel(const drltt_proto::HyperParameter& hyper_parameter,
               const drltt_proto::State& state)
      : BaseDynamicsModel(hyper_parameter, state) {}
  void Step(const drltt_proto::Action& action, float delta_t) override;
  ~BicycleModel() = default;

  bool get_state_observation(std::vector<float>* observation) const override;
  bool get_dynamics_model_observation(
      std::vector<float>* observation) const override;

 protected:
  void parse_hyper_parameter() override;
  static drltt_proto::State _compute_derivative(
      const drltt_proto::State& state, const drltt_proto::Action& action,
      const drltt_proto::HyperParameter& hyper_parameter);
};
}  // namespace drltt
