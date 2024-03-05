#include "policy_inference.h"
#include <gtest/gtest.h>
#include "drltt_proto/sdk/exported_policy_test_case.pb.h"

using namespace drltt;

TEST(PolicyInferenceTest, ForwardTest) {
    torch::Tensor tensor = torch::rand({2, 3});
    torch::jit::script::Module module;
    std::string module_path = "/drltt-work_dir/track-tiny/checkpoint/traced_policy.pt";
    module = torch::jit::load(module_path);
}
