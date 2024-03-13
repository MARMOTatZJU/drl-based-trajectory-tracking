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

typedef std::tuple<float, float, int, int> THRESHOLD_AND_COUNT;
typedef std::vector<THRESHOLD_AND_COUNT> THRESHOLDS_AND_COUNTS;
typedef std::tuple<bool, std::string> CHECK_RESULT;
typedef std::vector<CHECK_RESULT> CHECK_RESULTS;

/**
 * @brief Counter for counting success rate based on multiple thresholds.
 *
 * TODO: move to test_utils.[h|cpp]
 *
 */
class MultiThresholdCounter {
 public:
  MultiThresholdCounter() = default;
  ~MultiThresholdCounter() {}

  MultiThresholdCounter(const THRESHOLDS_AND_COUNTS& thresholds_and_counts) {
    _thresholds_and_counts = thresholds_and_counts;
  }

  bool Count(float diff) {
    for (int level_index = 0; level_index < _thresholds_and_counts.size();
         ++level_index) {
      auto& level_data = _thresholds_and_counts.at(level_index);
      const float threshold = std::get<0>(level_data);
      if (diff < threshold) {
        std::get<2>(level_data) = std::get<2>(level_data) + 1;
      }
      std::get<3>(level_data) = std::get<3>(level_data) + 1;
    }
    return true;
  }

  bool Check(CHECK_RESULTS& check_results) {
    check_results.clear();
    for (auto& level_data : _thresholds_and_counts) {
      const float thres_level = std::get<0>(level_data);
      const float pass_ratio_thres = std::get<1>(level_data);
      const float pass_count = std::get<2>(level_data);
      const float total_count = std::get<3>(level_data);
      const float pass_ratio =
          static_cast<float>(pass_count) / static_cast<float>(total_count);
      const bool pass_flag = (pass_ratio >= pass_ratio_thres);

      CHECK_RESULT check_result;
      // check flag
      std::get<0>(check_result) = pass_flag;
      // debug info
      // clang-format off
      std::get<1>(check_result) =
          "Threshold level " + std::to_string(thres_level) + " numeric precision check result:" + "\n"
        + "thres_level: " + std::to_string(thres_level) + " / " + "\n"
        + "pass_ratio_thres: " + std::to_string(pass_ratio_thres) + " / " + "\n"
        + "pass_count: " + std::to_string(pass_count) + " / " + "\n"
        + "total_count: " + std::to_string(total_count) + " / " + "\n"
        + "pass_ratio: " + std::to_string(pass_ratio) + "." + "\n" + "\n";
      // clang-format on

      check_results.push_back(check_result);
    }
    return true;
  }

 private:
  THRESHOLDS_AND_COUNTS _thresholds_and_counts;
};

TEST(EnvironmentsTest, TrajectoryTrackingTest) {
  const std::string checkpoint_dir = MACRO_CHECKPOINT_DIR;
  const std::string module_path = checkpoint_dir + "/traced_policy.pt";
  const std::string env_data_path = checkpoint_dir + "/env_data.bin";

  drltt_proto::Environment env_data;
  parse_proto_from_file(env_data, env_data_path);
  const int n_test_cases = env_data.trajectory_tracking().episodes().size();
  std::cerr << "Environment tested on " << n_test_cases << " cases."
            << std::endl;

  // numeric precision threshold/ratio/correct count/total count
  //  TODO: add to a class
  THRESHOLDS_AND_COUNTS test_thresholds_and_counts = {
      // clang-format off
      {1e-1, 0.980, 0, 0},
      {1e-2, 0.950, 0, 0},
      {1e-3, 0.900, 0, 0},
      {1e-4, 0.800, 0, 0},
      {1e-5, 0.600, 0, 0},
      // clang-format on
  };

  MultiThresholdCounter counter(test_thresholds_and_counts);

  for (int test_case_index = 0; test_case_index < n_test_cases;
       ++test_case_index) {
    const drltt_proto::TrajectoryTrackingEpisode& test_episode_data =
        env_data.trajectory_tracking().episodes().at(test_case_index);
    TrajectoryTracking env;
    env.LoadPolicy(module_path);
    env.LoadEnvData(env_data_path);
    env.set_dynamics_model_hyper_parameter(
        test_episode_data.selected_dynamics_model_index());
    env.set_reference_line(test_episode_data.reference_line());
    env.set_dynamics_model_initial_state(
        test_episode_data.dynamics_model().states().at(0));
    env.RollOut();
    TRAJECTORY tracked_trajectory = env.get_tracked_trajectory();

    // const float _EPSILON = 1e-3;

    // TODO: use both atol and rtol for close check
    // reference: https://pytorch.org/docs/stable/generated/torch.allclose.html
    for (int index = 0; index < test_episode_data.tracking_length(); ++index) {
      auto gt_data = test_episode_data.dynamics_model().states().at(index);
      auto rt_data = std::get<0>(tracked_trajectory).at(index);
      counter.Count(rt_data - gt_data);
      // EXPECT_LT((rt_data - gt_data), _EPSILON)
      //     << "============ STATE COMPARISON ============" << std::endl
      //     << "Test case: " << test_case_index << ", Step: " << index << ": "
      //     << std::endl
      //     << print_data(gt_data) << std::endl
      //     << print_data(rt_data) << std::endl;
    }
    for (int index = 0; index < test_episode_data.tracking_length(); ++index) {
      auto gt_data = test_episode_data.dynamics_model().actions().at(index);
      auto rt_data = std::get<1>(tracked_trajectory).at(index);
      counter.Count(rt_data - gt_data);
      // EXPECT_LT((rt_data - gt_data), _EPSILON)
      //     << "============ ACTION COMPARISON ============" << std::endl
      //     << "Test case: " << test_case_index << ", Step: " << index << ": "
      //     << std::endl
      //     << print_data(gt_data) << std::endl
      //     << print_data(rt_data) << std::endl;
    }
    for (int index = 0; index < test_episode_data.tracking_length(); ++index) {
      auto gt_data =
          test_episode_data.dynamics_model().observations().at(index);
      auto rt_data = std::get<2>(tracked_trajectory).at(index);
      counter.Count(rt_data - gt_data);
      // EXPECT_LT((rt_data - gt_data), _EPSILON)
      //     << "============ OBSERVATION COMPARISON ============" << std::endl
      //     << "Test case: " << test_case_index << ", Step: " << index << ": "
      //     << std::endl
      //     << print_data(gt_data) << std::endl
      //     << print_data(rt_data) << std::endl;
    }
    for (int index = 0; index < test_episode_data.tracking_length(); ++index) {
      auto gt_data =
          test_episode_data.dynamics_model().debug_infos().at(index).data();
      auto rt_data = std::get<3>(tracked_trajectory).at(index);
      int data_len = std::min(static_cast<int>(gt_data.size()),
                              static_cast<int>(rt_data.size()));
      if (data_len > 0) {
        std::cerr << "Test case: " << test_case_index << ", Step: " << index
                  << std::endl;
      }
      for (int data_index = 0; data_index < data_len; ++data_index) {
        std::cerr << "    gt_data: " << gt_data.at(data_index)
                  << ", rt_data: " << rt_data.at(data_index) << std::endl;
      }
    }
  }
  CHECK_RESULTS check_results;
  counter.Check(check_results);
  for (CHECK_RESULT& check_result : check_results) {
    const bool pass_flag = std::get<0>(check_result);
    const std::string check_info = std::get<1>(check_result);
    EXPECT_TRUE(pass_flag);
    std::cerr << check_info;
  }
}
