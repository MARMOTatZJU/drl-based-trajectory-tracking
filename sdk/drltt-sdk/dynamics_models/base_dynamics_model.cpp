#include "base_dynamics_model.h"

namespace drltt {

BaseDynamicsModel::BaseDynamicsModel(
    const drltt_proto::HyperParameter& hyper_parameter) {
  _hyper_parameter.CopyFrom(hyper_parameter);
  this->parse_hyper_parameter();
}

BaseDynamicsModel::BaseDynamicsModel(
    const drltt_proto::HyperParameter& hyper_parameter,
    const drltt_proto::State& init_state)
    : BaseDynamicsModel(hyper_parameter) {
  reset(init_state);
}

void BaseDynamicsModel::reset(const drltt_proto::State& state) {
  _state.CopyFrom(state);
}

drltt_proto::State BaseDynamicsModel::get_state() const {
  return _state;
}

bool BaseDynamicsModel::set_state(const drltt_proto::State& state) {
  _state.CopyFrom(state);
  return true;
}

drltt_proto::HyperParameter BaseDynamicsModel::get_hyper_parameter() const {
  return _hyper_parameter;
}

bool BaseDynamicsModel::set_hyper_parameter(
    const drltt_proto::HyperParameter& hyper_parameter) {
  _hyper_parameter.CopyFrom(hyper_parameter);
  return true;
}

}  // namespace drltt
