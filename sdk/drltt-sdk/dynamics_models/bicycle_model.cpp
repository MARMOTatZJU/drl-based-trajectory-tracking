#include "bicycle_model.h"

namespace drltt {

void BicycleModel::step(const drltt_proto::Action& action, float delta_t) {
  drltt_proto::State derivative =
      _compute_derivative(_state, action, _hyper_parameter);
  _state.mutable_bicycle_model()->CopyFrom(
      _state.bicycle_model() +
      derivative.bicycle_model() *
          delta_t);  // TODO move to canonical implementation `+=`
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

  float frontwheel_to_cog = hyper_parameter.bicycle_model().frontwheel_to_cog();
  float rearwheel_to_cog = hyper_parameter.bicycle_model().rearwheel_to_cog();

  float gravity_center_relative_position =
      rearwheel_to_cog / (rearwheel_to_cog + frontwheel_to_cog);

  float omega = std::atan(gravity_center_relative_position * std::tan(s));
  omega = normalize_angle(omega);

  float dx_dt = v * std::cos(r + omega);
  float dy_dt = v * std::sin(r + omega);
  float dr_dt = v / rearwheel_to_cog * std::sin(omega);
  float dv_dt = a;

  drltt_proto::State derivative;
  derivative.mutable_bicycle_model()->mutable_body_state()->set_x(dx_dt);
  derivative.mutable_bicycle_model()->mutable_body_state()->set_y(dy_dt);
  derivative.mutable_bicycle_model()->mutable_body_state()->set_r(dr_dt);
  derivative.mutable_bicycle_model()->set_v(dv_dt);

  return derivative;
}

}  // namespace drltt
