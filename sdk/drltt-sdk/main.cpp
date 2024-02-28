#include <iostream>
#include "common/protobuf_operators.h"
#include "drltt_proto/dynamics_model/basics.pb.h"
#include "drltt_proto/environment/trajectory_tracking.pb.h"

int main() {
  // drltt_proto::State* state = new drltt_proto::State();
  drltt_proto::BodyState state;
  drltt_proto::BodyState state2;
  state + state2;
  std::cout << state.x() << std::endl;
  std::cout << "marmot" << std::endl;
}
