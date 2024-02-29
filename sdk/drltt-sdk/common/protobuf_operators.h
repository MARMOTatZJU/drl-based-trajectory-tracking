#pragma once

#include "drltt_proto/dynamics_model/basics.pb.h"
#include "drltt_proto/dynamics_model/state.pb.h"

/**
 * Add two body state together. Perform normalization on heading.
 * @param lhs Left hand side body state.
 * @param rhs Right hand side body state.
 * @return Added body state
 */
drltt_proto::BodyState operator+(drltt_proto::BodyState lhs,
                                 const drltt_proto::BodyState& rhs);

/**
 * Scale a body state with a scalar to represent a difference in body state. No
 * normalization performed on heading in this case.
 * @param lhs Body state.
 * @param rhs Scalar.
 * @return Scaled body state.
 */
drltt_proto::BodyState operator*(drltt_proto::BodyState lhs, float rhs);


/**
 * Scale a body state with a scalar to represent a difference in body state. No
 * normalization performed on heading in this case.
 * @param lhs Scalar.
 * @param rhs Body state.
 * @return Scaled body state.
 */
drltt_proto::BodyState operator*(float lhs, drltt_proto::BodyState rhs);
