#include "bicycle_model.h"
#include <gtest/gtest.h>

using namespace drltt;

TEST(DynamicsModelTest, BicycleModelTest) {
  drltt_proto::HyperParameter hyper_parameter;
  hyper_parameter.mutable_bicycle_model()->set_front_overhang(0.9);
  hyper_parameter.mutable_bicycle_model()->set_rear_overhang(0.9);
  hyper_parameter.mutable_bicycle_model()->set_wheelbase(2.7);
  hyper_parameter.mutable_bicycle_model()->set_width(1.8);
  BicycleModel dynamics_model(hyper_parameter);
  drltt_proto::Action action;
  float delta_t = 0.1;
  dynamics_model.Step(action, delta_t);
}
