#include "trajectory_tracking.h"

namespace drltt {

bool TrajectoryTracking::LoadPolicy(const std::string& policy_path) {
  return _policy_model.Load(policy_path);
}

bool TrajectoryTracking::LoadEnvData(const std::string& env_data_path) {
  return parse_proto_from_file(_env_data, env_data_path);
}

bool TrajectoryTracking::set_dynamics_model_hyper_parameter(int index) {
  const google::protobuf::RepeatedPtrField<drltt_proto::HyperParameter>&
      all_hparams = _env_data.trajectory_tracking()
                        .hyper_parameter()
                        .dynamics_models_hyper_parameters();
  if (index >= 0 && index <= all_hparams.size()) {
    _dynamics_model.set_hyper_parameter(all_hparams.at(index));
    return true;
  } else {
    return false;
  }
}

bool TrajectoryTracking::set_reference_line(
    const std::vector<REFERENCE_WAYPOINT>& reference_line) {
  drltt_proto::ReferenceLine new_reference_line;
  for (const auto& it : reference_line) {
    drltt_proto::ReferenceLineWaypoint* reference_waypoint_ptr =
        new_reference_line.add_waypoints();
    reference_waypoint_ptr->set_x(std::get<0>(it));
    reference_waypoint_ptr->set_y(std::get<1>(it));
  }
  return set_reference_line(new_reference_line);
}

bool TrajectoryTracking::set_reference_line(
    const drltt_proto::ReferenceLine& reference_line) {
  _reference_line.CopyFrom(reference_line);

  drltt_proto::State init_state;
  EstimateInitialState(
      _reference_line, init_state,
      _env_data.trajectory_tracking().hyper_parameter().step_interval());
  _dynamics_model.set_state(init_state);

  return true;
}

// TODO: implement test
bool TrajectoryTracking::EstimateInitialState(
    const drltt_proto::ReferenceLine& reference_line, drltt_proto::State& state,
    float delta_t) {
  const int length = reference_line.waypoints().size();
  if (length <= 1) {
    std::cerr << "`reference_line` too short to estimate initial state.";
    return false;
  }

  const int window_size = 5;
  const float discount_factor = 1 / std::exp(1.0);
  const int real_window_size = std::min<int>(window_size, length);
  float total_displacement = 0;
  float total_displacement_x = 0;
  float total_displacement_y = 0;
  float total_coefficient = 0;

  const drltt_proto::ReferenceLineWaypoint init_waypoint =
      reference_line.waypoints().at(0);
  for (int index = 0; index < real_window_size - 1; ++index) {
    const drltt_proto::ReferenceLineWaypoint& current_waypoint =
        reference_line.waypoints().at(index);
    const drltt_proto::ReferenceLineWaypoint& next_waypoint =
        reference_line.waypoints().at(index + 1);
    const float coef = std::pow(discount_factor, index);
    total_displacement +=
        (std::hypot(next_waypoint.x() - current_waypoint.x(),
                    next_waypoint.y() - current_waypoint.y()) *
         coef);
    total_displacement_x += ((next_waypoint.x() - current_waypoint.x()) * coef);
    total_displacement_y += ((next_waypoint.y() - current_waypoint.y()) * coef);
    total_coefficient += coef;
  }

  const float init_r = std::atan2(total_displacement_y, total_displacement_x);
  const float init_v = total_displacement / total_coefficient / delta_t;

  state.mutable_bicycle_model()->mutable_body_state()->set_x(init_waypoint.x());
  state.mutable_bicycle_model()->mutable_body_state()->set_y(init_waypoint.y());
  state.mutable_bicycle_model()->mutable_body_state()->set_r(init_r);
  state.mutable_bicycle_model()->set_v(init_v);

  return true;
}

bool TrajectoryTracking::set_dynamics_model_initial_state(STATE state) {
  drltt_proto::State init_state;
  init_state.mutable_bicycle_model()->mutable_body_state()->set_x(
      std::get<0>(state));
  init_state.mutable_bicycle_model()->mutable_body_state()->set_y(
      std::get<1>(state));
  init_state.mutable_bicycle_model()->mutable_body_state()->set_r(
      std::get<2>(state));
  init_state.mutable_bicycle_model()->set_v(std::get<3>(state));
  return set_dynamics_model_initial_state(init_state);
}

bool TrajectoryTracking::set_dynamics_model_initial_state(
    drltt_proto::State state) {
  _dynamics_model.set_state(state);
  return true;
}

bool TrajectoryTracking::RollOut() {
  _states.clear();
  _actions.clear();
  _observation_manager.Reset(&_reference_line, &_dynamics_model);

  const int tracking_length = _reference_line.waypoints().size();
  const float step_interval =
      _env_data.trajectory_tracking().hyper_parameter().step_interval();
  const float n_observation_steps =
      _env_data.trajectory_tracking().hyper_parameter().n_observation_steps();
  for (int step_index = 0; step_index < tracking_length; ++step_index) {
    // state
    drltt_proto::State state = _dynamics_model.get_state();
    const drltt_proto::BodyState& body_state =
        state.bicycle_model().body_state();
    // observation
    std::vector<float> observation_vec;
    _observation_manager.get_observation(body_state, step_index,
                                         n_observation_steps, &observation_vec);
    drltt_proto::Observation observation;
    for (const auto scalar : observation_vec) {
      observation.mutable_bicycle_model()->add_feature(scalar);
    }
    // action
    std::vector<float> action_vec = _policy_model.Infer(observation_vec);
    drltt_proto::Action action;
    action.mutable_bicycle_model()->set_a(action_vec.at(0));
    action.mutable_bicycle_model()->set_s(action_vec.at(1));
    // record state, action, observation
    _states.push_back(state);
    _actions.push_back(action);
    _observations.push_back(observation);
    // step
    _dynamics_model.Step(action, step_interval);
  }
  return true;
}

TRAJECTORY TrajectoryTracking::get_tracked_trajectory() {
  // std::assert(_states.size() == _actions.size());
  const int trajectory_length = _states.size();
  TRAJECTORY trajectory;
  for (const auto& tracked_state : _states) {
    STATE state;
    std::get<0>(state) = tracked_state.bicycle_model().body_state().x();
    std::get<1>(state) = tracked_state.bicycle_model().body_state().y();
    std::get<2>(state) = tracked_state.bicycle_model().body_state().r();
    std::get<3>(state) = tracked_state.bicycle_model().v();
    std::get<0>(trajectory).push_back(state);
  }
  for (const auto& tracked_action : _actions) {
    ACTION action;
    std::get<0>(action) = tracked_action.bicycle_model().a();
    std::get<1>(action) = tracked_action.bicycle_model().s();
    std::get<1>(trajectory).push_back(action);
  }
  for (const auto& tracked_observation : _observations) {
    const auto& feature = tracked_observation.bicycle_model().feature();
    OBSERVATION observation(feature.begin(), feature.end());
    std::get<2>(trajectory).push_back(observation);
  }
  return trajectory;
}

}  // namespace drltt
