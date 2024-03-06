#include "trajectory_tracking.h"
#include <gtest/gtest.h>
#include "common/io.h"
#include "drltt_proto/environment/trajectory_tracking.pb.h"

using namespace drltt;

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
}