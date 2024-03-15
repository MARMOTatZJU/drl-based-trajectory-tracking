#pragma once

// TODO: verify if it is necessary
#define _USE_MATH_DEFINES

#include <algorithm>
#include <cmath>
#include "base_dynamics_model.h"

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
  drltt_proto::State _compute_derivative(
      const drltt_proto::State& state, const drltt_proto::Action& action,
      const drltt_proto::HyperParameter& hyper_parameter);
  float GetCogRelativePositionBetweenAxles() const;
  bool ComputeRotationRelatedVariables(float sterring_angle, float* omega,
                                       float* rotation_radius_inv) const;
  float GetMaxSteeringAngle() const;
};
}  // namespace drltt
