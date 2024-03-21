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
  /**
   * @brief Compute derivative w.r.t. time.
   *    TODO: use RVO to avoid copy.
   * @param state Dynamics model state.
   * @param action Dynamics model action.
   * @param hyper_parameter Dynamics model hyper parameter.
   * @return drltt_proto::State Derivative. Each field of the state represents
   * the derivative w.r.t. time of the field.
   */
  drltt_proto::State _compute_derivative(
      const drltt_proto::State& state, const drltt_proto::Action& action,
      const drltt_proto::HyperParameter& hyper_parameter);
  /**
   * @brief Get the relative position of Center of Gravity (CoG) between axles.
   *    The front axle represents 1.0, while the rear axle represents 0.0.
   *
   * @return float The relative position of CoG.
   */
  float GetCogRelativePositionBetweenAxles() const;
  /**
   * @brief Compute variables related to rotations.
   *
   * @param steering_angle Steering angle.
   * @param omega The angle between the speed direction of Center of Gravity
   * (CoG) and the vehicle heading.
   * @param rotation_radius_inv The inverse of rotation radius of vehicle under
   * current steering angle. Return the inverse for reasons of numerical
   * stability.
   * @return true Computation succeeded.
   * @return false Computation failed.
   */
  bool ComputeRotationRelatedVariables(float steering_angle, float* omega,
                                       float* rotation_radius_inv) const;
  /**
   * @brief Get the maximum steering angle. Based on current speed and the
   * maximum lateral acceleration.
   *
   * @return float The maximum steering angle.
   */
  float GetMaxSteeringAngle() const;
};
}  // namespace drltt
