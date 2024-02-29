#include "protobuf_operators.h"
#include <gtest/gtest.h>

TEST(BodyStateOperatorTest, BodyStateAdditionTest) {
  drltt_proto::BodyState state;
  state.set_x(0.);
  state.set_y(0.);
  state.set_r(0.);
  drltt_proto::BodyState state2;
  state2.set_x(1.);
  state2.set_y(1.);
  state2.set_r(1.);
  drltt_proto::BodyState state3 = state + state2;
  EXPECT_EQ(state3.x(), 1.0);
  EXPECT_EQ(state3.y(), 1.0);
  EXPECT_EQ(state3.r(), 1.0);
}

TEST(BodyStateOperatorTest, BodyStateMultiplicationTest) {
  drltt_proto::BodyState state;
  state.set_x(1.);
  state.set_y(1.);
  state.set_r(1.);
  float scalar = 3.0;
  drltt_proto::BodyState state2 = state * scalar;
  EXPECT_EQ(state2.x(), 3.0);
  EXPECT_EQ(state2.y(), 3.0);
  EXPECT_EQ(state2.r(), 3.0);
  drltt_proto::BodyState state3 = scalar * state;
  EXPECT_EQ(state3.x(), 3.0);
  EXPECT_EQ(state3.y(), 3.0);
  EXPECT_EQ(state3.r(), 3.0);
}
