#include "observation_manager.h"

namespace drltt {
bool ObservationManager::reset(drltt_proto::ReferenceLine* reference_line_ptr,
                               BaseDynamicsModel* dynamics_model_ptr) {
  if (reference_line_ptr == nullptr || dynamics_model_ptr == nullptr) {
    std::cerr << "nullptr found." << std::endl;
    return false;
  }
  _reference_line_ptr = reference_line_ptr;
  _dynamics_model_ptr = dynamics_model_ptr;
  return true;
}

bool ObservationManager::get_observation(
    const drltt_proto::BodyState& body_state, int start_index,
    int n_observation_steps, std::vector<float>* observation) {
  get_reference_line_observation(body_state, start_index, n_observation_steps,
                                 observation);
  _dynamics_model_ptr->get_state_observation(observation);
  _dynamics_model_ptr->get_dynamics_model_observation(observation);
  return true;
}

// TODO unit test with `env_data.bin`
bool ObservationManager::get_reference_line_observation(
    const drltt_proto::BodyState& body_state, int start_index,
    int n_observation_steps, std::vector<float>* observation) {
  // slice reference line segment
  std::vector<const drltt_proto::ReferenceLineWaypoint*> observed_waypoint_ptrs;
  const int reference_line_length = _reference_line_ptr->waypoints().size();
  for (int index = start_index; index < start_index + n_observation_steps;
       ++index) {
    if (index >= reference_line_length) {
      // padding at the end by repeating. TODO: support different type of
      // padding.
      const drltt_proto::ReferenceLineWaypoint& waypoint =
          _reference_line_ptr->waypoints().at(reference_line_length - 1);
      observed_waypoint_ptrs.push_back(&waypoint);
    } else {
      // normal observation
      const drltt_proto::ReferenceLineWaypoint& waypoint =
          _reference_line_ptr->waypoints().at(index);
      observed_waypoint_ptrs.push_back(&waypoint);
    }
  }
  // transform to body frame
  for (const auto& waypoint_ptr : observed_waypoint_ptrs) {
    drltt_proto::BodyState point;
    point.set_x(waypoint_ptr->x());
    point.set_y(waypoint_ptr->y());
    transform_to_local_from_world(body_state, &point);
    observation->push_back(point.x());
    observation->push_back(point.y());
  }
  return true;
}

}  // namespace drltt