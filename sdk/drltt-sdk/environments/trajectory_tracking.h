#pragma once

#include <cassert>
#include <cmath>
#include <tuple>
#include <vector>
#include "common/io.h"
#include "drltt-sdk/dynamics_models/bicycle_model.h"
#include "drltt-sdk/inference/policy_inference.h"
#include "drltt-sdk/managers/observation_manager.h"
#include "drltt_proto/dynamics_model/state.pb.h"
#include "drltt_proto/environment/trajectory_tracking.pb.h"
#include "drltt_proto/trajectory/trajectory.pb.h"

typedef std::tuple<float, float> REFERENCE_WAYPOINT;
typedef std::vector<REFERENCE_WAYPOINT> REFERENCE_LINE;
typedef std::tuple<float, float, float, float> STATE;
typedef std::tuple<float, float> ACTION;
typedef std::vector<float> OBSERVATION;
typedef std::tuple<std::vector<STATE>, std::vector<ACTION>,
                   std::vector<OBSERVATION>>
    TRAJECTORY;

namespace drltt {

// TODO: use factory to make it configurable
// TODO: verify if proto can be passed to python through pybind
class TrajectoryTracking {
 public:
  TrajectoryTracking() = default;
  ~TrajectoryTracking() {}
  bool load_policy(const std::string& policy_path);
  bool load_env_data(const std::string& env_data_path);
  bool set_dynamics_model_hyper_parameter(int index);
  bool set_reference_line(
      const std::vector<REFERENCE_WAYPOINT>& reference_line);
  bool set_reference_line(const drltt_proto::ReferenceLine& reference_line);
  static bool estimate_initial_state(
      const drltt_proto::ReferenceLine& reference_line,
      drltt_proto::State& state, float delta_t);
  bool set_dynamics_model_initial_state(STATE state);
  bool set_dynamics_model_initial_state(drltt_proto::State state);
  bool roll_out();
  TRAJECTORY get_tracked_trajectory();

 private:
  drltt_proto::State _estimate_init_state_from_reference_line(
      const drltt_proto::ReferenceLine&
          reference_line);  // avoid copy through RVO and std::move
  TorchJITModulePolicy _policy_model;
  drltt_proto::ReferenceLine _reference_line;
  drltt_proto::TrajectoryTrackingEnvironment _env_data;
  BicycleModel _dynamics_model;
  ObservationManager _observation_manager;
  std::vector<drltt_proto::State> _states;
  std::vector<drltt_proto::Action> _actions;
  std::vector<drltt_proto::Observation> _observations;
};

}  // namespace drltt
