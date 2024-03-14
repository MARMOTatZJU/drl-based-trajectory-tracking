#pragma once

#include <vector>
#include "drltt_proto/dynamics_model/action.pb.h"
#include "drltt_proto/dynamics_model/hyper_parameter.pb.h"
#include "drltt_proto/dynamics_model/state.pb.h"

namespace drltt {

class BaseDynamicsModel {
 public:
  BaseDynamicsModel() = default;
  BaseDynamicsModel(const drltt_proto::HyperParameter& hyper_parameter);
  BaseDynamicsModel(const drltt_proto::HyperParameter& hyper_parameter,
                    const drltt_proto::State& state);
  void Reset(const drltt_proto::State& state);
  virtual void Step(const drltt_proto::Action& action, float delta_t) {}
  drltt_proto::State get_state() const;
  bool set_state(const drltt_proto::State& state);
  // TODO: get_body_state() const

  drltt_proto::HyperParameter get_hyper_parameter() const;
  bool set_hyper_parameter(const drltt_proto::HyperParameter& hyper_parameter);

  ~BaseDynamicsModel() = default;

  // avoid copy by using RVO and std::move
  virtual bool get_state_observation(std::vector<float>* observation) const {
    return false;
  }
  virtual bool get_dynamics_model_observation(
      std::vector<float>* observation) const {
    return false;
  }

  drltt_proto::DebugInfo get_debug_info() { return _debug_info; }

 protected:
  virtual void parse_hyper_parameter() {}
  drltt_proto::State _state;
  drltt_proto::DebugInfo _debug_info;  // TODO: move to trajectory tracking env
  drltt_proto::HyperParameter _hyper_parameter;
};

}  // namespace drltt
