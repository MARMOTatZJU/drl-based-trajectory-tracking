#include <pybind11/pybind11.h>
#include <pybind11/stl.h>

#include "trajectory_tracker.h"

// TODO: export class directly
//    reference: https://pybind11.readthedocs.io/en/stable/classes.html
// TODO: add unit test for exported library
namespace py = pybind11;
using namespace drltt;

bool TrajectoryTrackerSetReferenceLine(TrajectoryTracker& trajectory_tracker,
                                       const REFERENCE_LINE& reference_line) {
  return trajectory_tracker.SetReferenceLine(reference_line);
}

bool TrajectoryTrackerSetDynamicsModelInitialState(
    TrajectoryTracker& trajectory_tracker, const STATE& init_state) {
  return trajectory_tracker.SetDynamicsModelInitialState(init_state);
}
TRAJECTORY TrajectoryTrackerTrackReferenceLine(
    TrajectoryTracker& trajectory_tracker) {
  return trajectory_tracker.TrackReferenceLine();
}

// Reference: https://pybind11.readthedocs.io/en/stable/classes.html
PYBIND11_MODULE(export_symbols, m) {
  m.doc() = "DRL-based Trajectory Tracking (DRLTT)";
  py::class_<TrajectoryTracker>(m, "TrajectoryTracker")
      .def(py::init<>())
      .def(py::init<const std::string&, int>());
  m.def("trajectory_tracker_set_reference_line",
        &TrajectoryTrackerSetReferenceLine);
  m.def("trajectory_tracker_set_dynamics_model_initial_state",
        &TrajectoryTrackerSetDynamicsModelInitialState);
  m.def("trajectory_tracker_track_reference_line",
        &TrajectoryTrackerTrackReferenceLine);
}
