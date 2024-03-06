#pragma once

#include <algorithm>
#include <cmath>
#include "drltt_proto/dynamics_model/state.pb.h"

// TODO: import from: https://github.com/ros/angles

/**
 * Normalize a scalar angle to [0, 2*pi).
 * Source: http://docs.ros.org/en/indigo/api/angles/html/angles_8h_source.html,
 * L68
 * @param angle Input angle.
 * @return Normalized angle.
 */
static inline double normalize_angle_positive(double angle) {
  return fmod(fmod(angle, 2.0 * M_PI) + 2.0 * M_PI, 2.0 * M_PI);
}

/**
 * Normalize a scalar angle to [-pi, pi).
 * Source: http://docs.ros.org/en/indigo/api/angles/html/angles_8h_source.html,
 * L81
 * @param angle Input angle.
 * @return Normalized angle.
 */
static inline double normalize_angle(double angle) {
  double a = normalize_angle_positive(angle);
  if (a >= M_PI)
    a -= 2.0 * M_PI;
  return a;
}

// TODO referenceline waypoint: move to body state
// TODO resolve c++ function naming issue
// TODO unit test
static inline void transform_to_local_from_world(
    const drltt_proto::BodyState& body_state, drltt_proto::BodyState* state) {
  const float x = body_state.x();
  const float y = body_state.y();
  const float r = body_state.r();

  const float transformed_x = std::cos(r) * state->x() +
                              std::sin(r) * state->y() - x * std::cos(r) -
                              y * std::sin(r);
  const float transformed_y = -std::sin(r) * state->x() +
                              std::cos(r) * state->y() + x * std::sin(r) -
                              y * std::cos(r);
  const float transformed_r = state->r() - r;

  state->set_x(transformed_x);
  state->set_y(transformed_y);
  state->set_r(transformed_r);
}
