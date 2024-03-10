#include "trajectory_tracker.h"

namespace drltt {
TrajectoryTracker::TrajectoryTracker(const std::string& load_path,
                                     int dynamics_model_index) {
  _env.LoadPolicy(load_path + "./traced_policy.pt");
  _env.LoadEnvData(load_path + "./env_data.bin");
  _env.set_dynamics_model_hyper_parameter(dynamics_model_index);
}

bool TrajectoryTracker::set_reference_line(
    const REFERENCE_LINE& reference_line) {
  return _env.set_reference_line(reference_line);
}

bool TrajectoryTracker::set_dynamics_model_initial_state(
    const STATE& init_state) {
  return _env.set_dynamics_model_initial_state(init_state);
}

TRAJECTORY TrajectoryTracker::TrackReferenceLine() {
  _env.RollOut();
  return _env.get_tracked_trajectory();
}

}  // namespace drltt
