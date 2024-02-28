#pragma once

#include "drltt_proto/dynamics_model/basics.pb.h"
#include "drltt_proto/dynamics_model/state.pb.h"

/**
 * Add to body state together. Perform normalization on heading.
 * @param lhs Left hand side body state.
 * @param rhs Right hand side body state.
 * @return Added body state
*/
drltt_proto::BodyState operator+(drltt_proto::BodyState lhs,
                                 const drltt_proto::BodyState& rhs);
