#include "protobuf_operators.h"

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

drltt_proto::BicycleModelState operator+(
    drltt_proto::BicycleModelState lhs,
    const drltt_proto::BicycleModelState& rhs) {
  lhs.mutable_body_state()->CopyFrom(lhs.body_state() + rhs.body_state());
  lhs.set_v(lhs.v() + rhs.v());

  return lhs;
}

drltt_proto::BicycleModelState operator*(drltt_proto::BicycleModelState lhs,
                                         float rhs) {
  lhs.mutable_body_state()->CopyFrom(lhs.body_state() * rhs);
  lhs.set_v(lhs.v() * rhs);

  return lhs;
}

drltt_proto::BicycleModelState operator*(float lhs,
                                         drltt_proto::BicycleModelState rhs) {
  return rhs * lhs;
}
