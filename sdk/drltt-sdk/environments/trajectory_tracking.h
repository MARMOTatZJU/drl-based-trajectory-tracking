/**
 * @file trajectory_tracking.h
 * @brief Trajectory tracking environment.
 *
 */
#pragma once

#include <cassert>
#include <cmath>
#include <tuple>
#include <vector>
#include "drltt-sdk/common/common.h"
#include "drltt-sdk/dynamics_models/bicycle_model.h"
#include "drltt-sdk/inference/policy_inference.h"
#include "drltt-sdk/managers/observation_manager.h"
#include "drltt_proto/dynamics_model/state.pb.h"
#include "drltt_proto/environment/environment.pb.h"
#include "drltt_proto/trajectory/trajectory.pb.h"

typedef std::tuple<float, float> REFERENCE_WAYPOINT;
typedef std::vector<REFERENCE_WAYPOINT> REFERENCE_LINE;
typedef std::tuple<float, float, float, float> STATE;
typedef std::tuple<float, float> ACTION;
typedef std::vector<float> OBSERVATION;
typedef std::vector<float> DEBUG_DATA;
typedef std::tuple<std::vector<STATE>, std::vector<ACTION>,
                   std::vector<OBSERVATION>, std::vector<DEBUG_DATA>>
    TRAJECTORY;

namespace drltt {

// TODO: use factory to make it configurable
// TODO: verify if proto can be passed to python through pybind
/**
 * @brief Trajectory tracking environment.
 *
 * Class for managing dynamics models/reference lines/policy model/etc. and
 * performing rollouts.
 *
 */
class TrajectoryTracking {
 public:
  TrajectoryTracking() = default;
  ~TrajectoryTracking() {}
  /**
   * @brief Load the underlying policy.
   *
   * @param policy_path Path to the policy.
   * @return true Loading succeeded.
   * @return false Loading failed.
   */
  bool LoadPolicy(const std::string& policy_path);
  /**
   * @brief Load the environment data.
   *
   * @param env_data_path Path to the protobuf binary file of environment data.
   * @return true Loading succeeded.
   * @return false Loading failed.
   */
  bool LoadEnvData(const std::string& env_data_path);
  /**
   * @brief Set the dynamics model hyper parameter with index.
   *    TODO: provide function to set dynamics model by name.
   *
   * @param index The index of dynamicsmo stored in the `env_data`.
   * @return true Setting succeeded.
   * @return false Setting failed.
   */
  bool set_dynamics_model_hyper_parameter(int index);
  /**
   * @brief Set the reference line object.
   *
   * @param reference_line Reference line.
   * @return true Setting succeeded.
   * @return false Setting failed.
   */
  bool set_reference_line(
      const std::vector<REFERENCE_WAYPOINT>& reference_line);
  /**
   * @brief Set the reference line object.
   *
   * @param reference_line Reference line.
   * @return true Setting succeeded.
   * @return false Setting failed.
   */
  bool set_reference_line(const drltt_proto::ReferenceLine& reference_line);
  /**
   * @brief Estimate the initial state.
   *
   * @param reference_line Reference line.
   * @param state The returned initial state.
   * @param delta_t Step interval.
   * @return true Setting succeeded.
   * @return false Setting failed.
   */
  static bool EstimateInitialState(
      const drltt_proto::ReferenceLine& reference_line,
      drltt_proto::State& state, float delta_t);
  /**
   * @brief Set the dynamics model initial state object.
   *
   * @param state Initial state to be set to dynamics model.
   * @return true Setting succeeded.
   * @return false Setting failed.
   */
  bool set_dynamics_model_initial_state(STATE state);
  /**
   * @brief Set the dynamics model initial state object.
   *
   * @param state Initial state to be set to dynamics model.
   * @return true Setting succeeded.
   * @return false Setting failed.
   */
  bool set_dynamics_model_initial_state(drltt_proto::State state);
  /**
   * @brief Roll out a trajectory based on underlying policy model and
   * environment.
   *
   * @return true Roll-out succeeded.
   * @return false Roll-out failed.
   */
  bool RollOut();
  /**
   * @brief Get the tracked trajectory object
   *
   * @return TRAJECTORY Tracked trajectory, format=<vector<STATE>,,
   * vector<ACTION>, vector<OBSERVATION>>
   */
  TRAJECTORY get_tracked_trajectory();

 private:
  TorchJITModulePolicy _policy_model;
  drltt_proto::ReferenceLine _reference_line;
  drltt_proto::Environment _env_data;
  BicycleModel _dynamics_model;
  ObservationManager _observation_manager;
  std::vector<drltt_proto::State> _states;
  std::vector<drltt_proto::Action> _actions;
  std::vector<drltt_proto::Observation> _observations;
  std::vector<drltt_proto::DebugInfo> _debug_infos;
};

}  // namespace drltt
