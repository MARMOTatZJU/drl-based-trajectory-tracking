#include "policy_inference.h"
#include <gtest/gtest.h>
#include <fstream>
#include <iostream>
#include <vector>
#include "common/io.h"
#include "drltt_proto/sdk/exported_policy_test_case.pb.h"

using namespace drltt;

TEST(PolicyInferenceTest, ForwardTest) {
  const std::string module_path =
      "/drltt-work_dir/track-tiny/checkpoint/traced_policy.pt";
  const std::string test_cases_path =
      "/drltt-work_dir/track-tiny/checkpoint/traced_policy_test_cases.bin";

  // load test case data
  drltt_proto::ExportedPolicyTestCases test_cases_proto;
  {
    std::fstream input(test_cases_path, std::ios::in | std::ios::binary);
    if (!input) {
      std::cout << test_cases_path << "not found!!!" << std::endl;
      FAIL();
    } else if (!test_cases_proto.ParseFromIstream(&input)) {
      std::string err_msg =
          "drltt_proto::ExportedPolicyTestCases parsing error.";
      std::cout << err_msg << std::endl;
      FAIL();
    }
    input.close();
  }
  torch::Tensor gt_observations_tensor =
      parse_tensor_proto_to_torch_tensor(test_cases_proto.observations());
  torch::Tensor gt_actions_tensor =
      parse_tensor_proto_to_torch_tensor(test_cases_proto.actions());

  // perform inference
  TorchJITModulePolicy policy;
  policy.load(module_path);
  torch::Tensor jit_actions_tensor = policy.infer(gt_observations_tensor);

  // check result
  const float atol = 1e-5;
  const float rtol = 1e-3;
  const bool all_close =
      torch::allclose(jit_actions_tensor, gt_actions_tensor, atol, rtol);
  EXPECT_TRUE(all_close);
  torch::Tensor isclose =
      torch::isclose(jit_actions_tensor, gt_actions_tensor, atol, rtol);
  const float isclose_ratio =
      static_cast<float>(torch::sum(isclose).item<int64_t>()) /
      static_cast<float>(isclose.numel());
  const float isclose_ratio_thres = 0.95;
  EXPECT_GT(isclose_ratio, isclose_ratio_thres);
}
