#pragma once

#include "protobuf_operators.h"

drltt_proto::BodyState operator+(drltt_proto::BodyState lhs,
                                 const drltt_proto::BodyState& rhs) {
  lhs.set_x(lhs.x() + rhs.x());
  lhs.set_y(lhs.y() + rhs.y());
  lhs.set_r(lhs.r() + rhs.r());

  return lhs;
}
