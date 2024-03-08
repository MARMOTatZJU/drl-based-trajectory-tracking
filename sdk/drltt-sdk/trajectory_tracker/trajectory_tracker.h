#pragma once

#include "drltt-sdk/environments/trajectory_tracking.h"

namespace drltt {
class TrajectoryTracker {
 public:
  TrajectoryTracker() = default;
  ~TrajectoryTracker() {};

  TrajectoryTracker(const std::string& load_path, int dynamics_model_index);
  bool SetReferenceLine(const REFERENCE_LINE& reference_line);
  bool SetDynamicsModelInitialState(const STATE& init_state);
  TRAJECTORY TrackReferenceLine();

 private:
  TrajectoryTracking _env;
};
}  // namespace drltt
