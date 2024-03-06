#include "trajectory_tracking.h"
#include <gtest/gtest.h>
#include <algorithm>
#include <iostream>
#include <sstream>
#include "common/io.h"
#include "drltt_proto/environment/trajectory_tracking.pb.h"

using namespace drltt;

// TODO move this part to another source file
float operator-(const STATE& lhs, const drltt_proto::State& rhs) {
  return std::max<float>(
      {std::fabs(std::get<0>(lhs) - rhs.bicycle_model().body_state().x()),
       std::fabs(std::get<1>(lhs) - rhs.bicycle_model().body_state().y()),
       std::fabs(std::get<2>(lhs) - rhs.bicycle_model().body_state().r()),
       std::fabs(std::get<3>(lhs) - rhs.bicycle_model().v())});
}

float operator-(const ACTION& lhs, const drltt_proto::Action& rhs) {
  return std::max<float>(
      {std::fabs(std::get<0>(lhs) - rhs.bicycle_model().a()),
       std::fabs(std::get<1>(lhs) - rhs.bicycle_model().s())});
}

float operator-(const OBSERVATION& lhs, const drltt_proto::Observation& rhs) {
  const auto& lhs_vec = lhs;
  const auto& rhs_vec = rhs.bicycle_model().feature();
  EXPECT_EQ(lhs_vec.size(), rhs_vec.size());
  const int max_index = lhs_vec.size();
  std::vector<float> diffs_vec;
  for (int index = 0; index < max_index; ++index) {
    diffs_vec.push_back(std::fabs(lhs_vec.at(index) - rhs_vec.at(index)));
  }
  return *std::max_element(diffs_vec.begin(), diffs_vec.end());
}

std::string print_data(const STATE& state) {
  std::stringstream ss;
  ss << "(";
  ss << std::get<0>(state);
  ss << ", ";
  ss << std::get<1>(state);
  ss << ", ";
  ss << std::get<2>(state);
  ss << ", ";
  ss << std::get<3>(state);
  ss << ")";
  return ss.str();
}

std::string print_data(const drltt_proto::State& state) {
  std::stringstream ss;
  ss << "(";
  ss << state.bicycle_model().body_state().x();
  ss << ", ";
  ss << state.bicycle_model().body_state().y();
  ss << ", ";
  ss << state.bicycle_model().body_state().r();
  ss << ", ";
  ss << state.bicycle_model().v();
  ss << ")";
  return ss.str();
}

std::string print_data(const ACTION& action) {
  std::stringstream ss;
  ss << "(";
  ss << std::get<0>(action);
  ss << ", ";
  ss << std::get<1>(action);
  ss << ")";
  return ss.str();
}

std::string print_data(const drltt_proto::Action& action) {
  std::stringstream ss;
  ss << "(";
  ss << action.bicycle_model().a();
  ss << ", ";
  ss << action.bicycle_model().s();
  ss << ")";
  return ss.str();
}

std::string print_data(const OBSERVATION& observation) {
  std::stringstream ss;
  ss << "(";
  for (auto obs = observation.begin(); obs != observation.end(); ++obs) {
    if (obs != observation.begin()) {
      ss << ", ";
    }
    ss << *obs;
  }
  ss << ")";
  return ss.str();
}

std::string print_data(const drltt_proto::Observation& observation) {
  std::stringstream ss;
  ss << "(";
  const auto& feature = observation.bicycle_model().feature();
  for (auto obs = feature.begin(); obs != feature.end(); ++obs) {
    if (obs != feature.begin()) {
      ss << ", ";
    }
    ss << *obs;
  }
  ss << ")";
  return ss.str();
}

TEST(EnvironmentsTest, TrajectoryTrackingTest) {

  const std::string module_path =
      "/drltt-work_dir/track-test/checkpoint/traced_policy.pt";
  const std::string env_data_path =
      "/drltt-work_dir/track-test/checkpoint/env_data.bin";

  drltt_proto::TrajectoryTrackingEnvironment env_data;
  parse_proto_from_file(env_data, env_data_path);

  // build and setup environment
  const drltt_proto::TrajectoryTrackingEpisode test_episode_data =
      env_data.episode();
  TrajectoryTracking env;
  env.load_policy(module_path);
  env.load_env_data(env_data_path);
  env.set_dynamics_model_hyper_parameter(
      test_episode_data.selected_dynamics_model_index());
  env.set_reference_line(test_episode_data.reference_line());
  env.set_dynamics_model_initial_state(
      test_episode_data.dynamics_model().states().at(0));
  env.roll_out();
  TRAJECTORY tracked_trajectory = env.get_tracked_trajectory();

  const float EPSILON = 1e-4;
  // TODO: use both atol and rtol for close check
  // reference: https://pytorch.org/docs/stable/generated/torch.allclose.html
  for (int index = 0; index < env_data.episode().tracking_length(); ++index) {
    auto gt_data = env_data.episode().dynamics_model().states().at(index);
    auto rt_data = std::get<0>(tracked_trajectory).at(index);
    EXPECT_LT((rt_data - gt_data), EPSILON)
        << "============ STATE COMPARISON ============" << std::endl
        << "Step: " << index << ": " << std::endl
        << print_data(gt_data) << std::endl
        << print_data(rt_data) << std::endl;
  }
  for (int index = 0; index < env_data.episode().tracking_length(); ++index) {
    auto gt_data = env_data.episode().dynamics_model().actions().at(index);
    auto rt_data = std::get<1>(tracked_trajectory).at(index);
    EXPECT_LT((rt_data - gt_data), EPSILON)
        << "============ ACTION COMPARISON ============" << std::endl
        << "Step: " << index << ": " << std::endl
        << print_data(gt_data) << std::endl
        << print_data(rt_data) << std::endl;
  }
  for (int index = 0; index < env_data.episode().tracking_length(); ++index) {
    auto gt_data = env_data.episode().dynamics_model().observations().at(index);
    auto rt_data = std::get<2>(tracked_trajectory).at(index);
    EXPECT_LT((rt_data - gt_data), EPSILON)
        << "============ OBSERVATION COMPARISON ============" << std::endl
        << "Step: " << index << ": " << std::endl
        << print_data(gt_data) << std::endl
        << print_data(rt_data) << std::endl;
  }
}
