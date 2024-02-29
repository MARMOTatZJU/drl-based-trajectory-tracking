#pragma once

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
  void reset(const drltt_proto::State& state);
  virtual void step(const drltt_proto::Action& action, float delta_t) {}
  drltt_proto::State get_state();

  ~BaseDynamicsModel() = default;

 protected:
  virtual void parse_hyper_parameter() {}
  drltt_proto::State _state;
  drltt_proto::HyperParameter _hyper_parameter;
};

}  // namespace drltt
