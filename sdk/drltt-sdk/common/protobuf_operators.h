#pragma once

#include "drltt_proto/dynamics_model/basics.pb.h"
#include "drltt_proto/dynamics_model/state.pb.h"

drltt_proto::BodyState operator+(drltt_proto::BodyState lhs,
                                 const drltt_proto::BodyState& rhs);
