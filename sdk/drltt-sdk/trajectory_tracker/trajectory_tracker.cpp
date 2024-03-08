#include "trajectory_tracker.h"

namespace drltt {
TrajectoryTracker::TrajectoryTracker(const std::string& load_path,
                                     int dynamics_model_index) {
  _env.load_policy(load_path + "./traced_policy.pt");
  _env.load_env_data(load_path + "./env_data.bin");
  _env.set_dynamics_model_hyper_parameter(dynamics_model_index);
}

bool TrajectoryTracker::SetReferenceLine(const REFERENCE_LINE& reference_line) {
  return _env.set_reference_line(reference_line);
}

bool TrajectoryTracker::SetDynamicsModelInitialState(const STATE& init_state) {
  return _env.set_dynamics_model_initial_state(init_state);
}

TRAJECTORY TrajectoryTracker::TrackReferenceLine() {
  _env.roll_out();
  return _env.get_tracked_trajectory();
}

}  // namespace drltt
