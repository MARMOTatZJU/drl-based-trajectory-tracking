#include "bicycle_model.h"

namespace drltt {

void BicycleModel::Step(const drltt_proto::Action& action, float delta_t) {
  _debug_info.mutable_data()->Clear();  // consider a more "automatic" way to clear

  drltt_proto::State derivative =
      _compute_derivative(_state, action, _hyper_parameter);
  _state.mutable_bicycle_model()->CopyFrom(
      _state.bicycle_model() +
      derivative.bicycle_model() *
          delta_t);  // TODO move to canonical implementation `+=`
}

bool BicycleModel::get_state_observation(
    std::vector<float>* observation) const {
  observation->push_back(_state.bicycle_model().v());
  observation->push_back(GetMaxSteeringAngle());

  return true;
}

bool BicycleModel::get_dynamics_model_observation(
    std::vector<float>* observation) const {
  observation->push_back(_hyper_parameter.bicycle_model().front_overhang());
  observation->push_back(_hyper_parameter.bicycle_model().wheelbase());
  observation->push_back(_hyper_parameter.bicycle_model().rear_overhang());
  observation->push_back(_hyper_parameter.bicycle_model().width());
  observation->push_back(_hyper_parameter.bicycle_model().length());
  observation->push_back(_hyper_parameter.bicycle_model().max_lat_acc());

  return true;
}

void BicycleModel::parse_hyper_parameter() {
  float front_overhang = _hyper_parameter.bicycle_model().front_overhang();
  float wheelbase = _hyper_parameter.bicycle_model().wheelbase();
  float rear_overhang = _hyper_parameter.bicycle_model().rear_overhang();
  float length = front_overhang + wheelbase + rear_overhang;
  _hyper_parameter.mutable_bicycle_model()->set_length(length);
  _hyper_parameter.mutable_bicycle_model()->set_frontwheel_to_cog(
      wheelbase + rear_overhang - length / 2);
  _hyper_parameter.mutable_bicycle_model()->set_rearwheel_to_cog(
      wheelbase + front_overhang - length / 2);
}

drltt_proto::State BicycleModel::_compute_derivative(
    const drltt_proto::State& state, const drltt_proto::Action& action,
    const drltt_proto::HyperParameter& hyper_parameter) {
  float x = state.bicycle_model().body_state().x();
  float y = state.bicycle_model().body_state().y();
  float r = state.bicycle_model().body_state().r();
  float v = state.bicycle_model().v();
  float a = action.bicycle_model().a();
  float s = action.bicycle_model().s();

  // clip s
  const float max_steer = GetMaxSteeringAngle();
  s = clip(s, -max_steer, +max_steer);

  float omega;
  float rotation_radius_inv;
  ComputeRotationRelatedVariables(s, &omega, &rotation_radius_inv);

  float dx_dt = v * std::cos(r + omega);
  float dy_dt = v * std::sin(r + omega);
  float dr_dt = v * rotation_radius_inv;
  float dv_dt = a;

  drltt_proto::State derivative;
  derivative.mutable_bicycle_model()->mutable_body_state()->set_x(dx_dt);
  derivative.mutable_bicycle_model()->mutable_body_state()->set_y(dy_dt);
  derivative.mutable_bicycle_model()->mutable_body_state()->set_r(dr_dt);
  derivative.mutable_bicycle_model()->set_v(dv_dt);

  return derivative;
}

float BicycleModel::GetCogRelativePositionBetweenAxles() const {
  const float frontwheel_to_cog =
      _hyper_parameter.bicycle_model().frontwheel_to_cog();
  const float rearwheel_to_cog =
      _hyper_parameter.bicycle_model().rearwheel_to_cog();

  return rearwheel_to_cog / (rearwheel_to_cog + frontwheel_to_cog);
}

bool BicycleModel::ComputeRotationRelatedVariables(
    float steering_angle, float* omega, float* rotation_radius_inv) const {
  const float cog_relative_position_between_axles =
      GetCogRelativePositionBetweenAxles();
  *omega =
      std::atan(cog_relative_position_between_axles * std::tan(steering_angle));
  *omega = normalize_angle(*omega);
  // Return the inverse of the radius to ensure numerical stability.
  *rotation_radius_inv =
      std::sin(*omega) / _hyper_parameter.bicycle_model().rearwheel_to_cog();

  return true;
}

float BicycleModel::GetMaxSteeringAngle() const {
  const float max_lat_acc = _hyper_parameter.bicycle_model().max_lat_acc();
  const float v = _state.bicycle_model().v();
  const float rearwheel_to_cog =
      _hyper_parameter.bicycle_model().rearwheel_to_cog();

  float max_s;

  const float asin_arg =
      rearwheel_to_cog * max_lat_acc / std::max(v * v, EPSILON);

  if (asin_arg <= 1.0) {
    max_s = std::atan(std::tan(std::asin(asin_arg)) /
                      GetCogRelativePositionBetweenAxles());
  } else {
    max_s = M_PI;
  }

  return max_s;
}

}  // namespace drltt
