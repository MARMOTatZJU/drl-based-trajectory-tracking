#include "protobuf_operators.h"
#include "geometry.h"

drltt_proto::BodyState operator+(drltt_proto::BodyState lhs,
                                 const drltt_proto::BodyState& rhs) {
  lhs.set_x(lhs.x() + rhs.x());
  lhs.set_y(lhs.y() + rhs.y());
  lhs.set_r(normalize_angle(lhs.r() + rhs.r()));

  return lhs;
}

drltt_proto::BodyState operator*(drltt_proto::BodyState lhs, float rhs) {
  lhs.set_x(lhs.x() * rhs);
  lhs.set_y(lhs.y() * rhs);
  lhs.set_r(lhs.r() * rhs);

  return lhs;
}

drltt_proto::BodyState operator*(float lhs, drltt_proto::BodyState rhs) {

  return rhs * lhs;
}
