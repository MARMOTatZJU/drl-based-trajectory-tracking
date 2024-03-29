/**
 * @file trajectory_tracker.h
 * @brief Trajectory tracker exported SDK.
 *
 */
#pragma once

#include "drltt-sdk/environments/trajectory_tracking.h"

/**
 * drltt
 */
namespace drltt {
// clang-format off
/**
 * @brief DRLTT Trajectory Tracking C++ SDK.
 *
 * Nomenclature for documentation:
 *
 * - x: X-coordinate in [m] within (-inf, +inf).
 * - y: Y-coordinate in [m] within (-inf, +inf).
 * - r: heading in [rad] within [-pi, pi), following convention of math lib like `std::atan2`.
 * - v: scalar speed in [m/s] within [0, +inf)。
 * - a: acceleration in [m/s/s] within [0, +inf)。
 * - s: steering angle in [rad] within [-max_s, +max_s] where `max_s` is the steering limit.
 * 
 * TODO: move this part to the doc. of protobuf.
 *
 * Predefined type for documentation
 *
 * - STATE                : tuple<float x, float y, float r, float v>, state of dynamics model.
 * - ACTION               : tuple<float a, float s>, action of dynamics model.
 * - OBSERVATION          : vector<float>, vectorized observation feature.
 * - REFERENCE_WAYPOINT   : tuple<float x, float y>, vectorized observation feature.
 * - REFERENCE_LINE       : vector<REFERENCE_WAYPOINT>, reference line for the dynamics model to track.
 */
// clang-format on
class TrajectoryTracker {

 public:
  TrajectoryTracker() = default;
  ~TrajectoryTracker() {};

  /**
   * @param load_path  Path to checkpoint. See "Checkpoint Structure" in
   * `./README.md` for detail.
   * @param dynamics_model_index The index of dynamics model. The order
   * corresponds to the `dynamics_model_configs` within the config YAML in the
   * checkpoint folder.
   */
  TrajectoryTracker(const std::string& load_path, int dynamics_model_index);
  /**
   * @brief Set a reference line.
   *
   * It will estimate an initial state of the dynamics
   * model, which may be overwritten by other function later if necessary.
   *
   * @param reference_line Reference line to be tracked.
   * @return Success flag.
   */
  bool set_reference_line(const REFERENCE_LINE& reference_line);
  /**
   * @brief Set the Dynamics Model Initial State object.
   *
   * @param init_state Initial state.
   * @return true Setting succeeded.
   * @return false Setting failed.
   */
  bool set_dynamics_model_initial_state(const STATE& init_state);
  /**
   * @brief Perform trajectory tracking.
   *
   * Roll out a trajectory and return the tracked trajectory.
   *
   * @return Trajectory containing states, actions, and observations of the
   * roll-out. Format=<vector<STATE>, vector<ACTION>, vector<OBSERVATION>>.
   */
  TRAJECTORY TrackReferenceLine();

 private:
  TrajectoryTracking _env;
};
}  // namespace drltt
