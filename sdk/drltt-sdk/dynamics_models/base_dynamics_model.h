#pragma once

#include <vector>
#include "drltt-sdk/common/common.h"
#include "drltt_proto/dynamics_model/action.pb.h"
#include "drltt_proto/dynamics_model/hyper_parameter.pb.h"
#include "drltt_proto/dynamics_model/state.pb.h"

namespace drltt {

class BaseDynamicsModel {
 public:
  BaseDynamicsModel() = default;
  /**
   * @brief Construct a new Base Dynamics Model object
   *
   * @param hyper_parameter Hyper-parameter.
   */
  BaseDynamicsModel(const drltt_proto::HyperParameter& hyper_parameter);
  /**
   * @brief Construct a new Base Dynamics Model object
   *
   * @param hyper_parameter Hyper-parameter.
   * @param state Initial state.
   */
  BaseDynamicsModel(const drltt_proto::HyperParameter& hyper_parameter,
                    const drltt_proto::State& state);
  /**
   * @brief Reset the environment.
   *
   * @param state Initial state.
   */
  void Reset(const drltt_proto::State& state);
  /**
   * @brief Perform a forward step with the given action,
   *
   * @param action Action.
   * @param delta_t Step interval in [s].
   */
  virtual void Step(const drltt_proto::Action& action, float delta_t) {}
  /**
   * @brief Get the state object.
   *
   * @return drltt_proto::State State proto.
   */
  drltt_proto::State get_state() const;
  /**
   * @brief Set the state object
   *
   * @param state State used for setting.
   * @return true Setting succeeded.
   * @return false Setting failed.
   */
  bool set_state(const drltt_proto::State& state);
  // TODO: get_body_state() const
  /**
   * @brief Get the hyper parameter object.
   *
   * @return drltt_proto::HyperParameter Hyper-parameter proto.
   */
  drltt_proto::HyperParameter get_hyper_parameter() const;
  /**
   * @brief Set the hyper parameter object
   *
   * @param hyper_parameter Hyper-parameter used for setting.
   * @return true Setting succeeded.
   * @return false Setting failed.
   */
  bool set_hyper_parameter(const drltt_proto::HyperParameter& hyper_parameter);

  ~BaseDynamicsModel() = default;

  // avoid copy by using RVO and std::move
  /**
   * @brief Get the state observation object.
   *
   * @param observation The returned observation.
   * @return true
   * @return false
   */
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
