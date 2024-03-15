# DRL-Based Trajectory Tracking (DRLTT)

This repo hosts code and script for training and deploying the *DRL-Based Trajectory Tracking (DRLTT)* algorithm. DRLTT leverages Deep Reinforcement Learning (DRL) and achieves robustness, accuracy, and versatility in the Trajectory Tracking (TT) task in the context of Autonomous Driving. Benefiting from its methodological simplicity, DRLTT can process 32 trajectories (each contains 50 steps) within several milliseconds on edge computing devices.

Currently, DRLTT supports the following features:

* A Python framework
  * Training-Evaluation-Tracing of an RL policy for the task of Trajectory Tracking in Autonomous Driving.
  * Based on *Stable Baselines 3*.
  * See `./simulator`.
* A C++ SDK
  * Easy deployment and efficient inference of RL policy under a pure CPU environment.
  * Based on cpu-compiled *libtorch*.
  * See `./sdk`
* A Python SDK
  * Compatible with any Python environment, *No requirement* for any Python package.
  * Based on *pybind*.
  * See `./sdk/drltt-sdk/trajectory_tracker`


Please refer to the [*Code Repository*](https://github.com/MARMOTatZJU/drl-based-trajectory-tracking/) and the [*Technical Report*](https://arxiv.org/abs/2308.15991) for details.

The [Documentation](https://drl-based-trajectory-tracking.readthedocs.io/) hosted by [Read the Docs](https://readthedocs.org/) would also be helpful for our readers.

## Installation

### Python Requirements

DRLTT requires Python>=3.12. If you are using [Conda](https://www.anaconda.com/) for Python environment management, you may create an environment for DRLTT through the following command:

```bash
conda create --name drltt python=3.12
```

Install Python requirement through `pip`:

```bash
pip install -r requirements/pypi.txt
```

For network environments within Mainland China, you may consider using a domestic pip source to accelerate this process:

```bash
# Example using TUNA PyPI source
pip install -r requirements/pypi.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
```

### Protobuf Compiler

```bash
source install-setup-protoc.sh
```

## RL Training & Evaluating & Tracing

Run `./scripts/train_eval_trace-track.sh` for training-evaluation-tracing.

.. literalinclude:: ../../../scripts/train_eval_trace-track.sh
  :language: bash

Feel free to try out other scripts under `./scripts`

The checkpoint (trained model/log/evaluation results/etc.) will be output at `$work_dir/checkpoint/`.

### Checkpoint Structure

```text
├── 00-config-....yaml              # base config
├── 01-config-....yaml              # overriding config
├── ...
├── config.yaml                     # overridden configuration
├── checkpoint.zip                  # checkpoint of SB3
├── env_data.bin                    # environment data serialized in proto binary stream
├── traced_policy.pt                # traced policy, ready for SDK inference
├── traced_policy_test_cases.bin    # data of test cases for testing traced policy during deployment phase
├── log.txt                         # python logger's output
├── metrics.json                    # metrics
├── sb3-train                       # SB3 log during training phase
│   └── ...
└── sb3-eval                        # SB3 log during evaluation phase
    └── ...
```

### System Design of Python-Side Framework

```text
SB3-BaseAlgorithm
├── SB3 hyper-parameter
├── SB3 components
└── TrajectoryTrackingEnv
    ├── observation_space
    ├── action_space
    ├── ObservationManager
    │   ├── ReferenceLineManager
    │   │   └── ReferenceLine
    │   └── DynamicsModelManager
    │       List[DynamicsModel]
    │           ├── HyperParameter
    │           ├── State
    │           ├── Action
    │           └── step()
    ├── reset()
    │   └── random_walk()
    └── step()
        └── compute_reward()
```


## C++/Python SDK

See *DRTLL SDK* for details.

## Development

### Testing

Run `./test.sh` to test all code:

.. literalinclude:: ../../../test.sh
  :language: bash

Python testing is done with *pytest*. To launch the Python testing, run `./test-python.sh`:

.. literalinclude:: ../../../test-python.sh
  :language: bash

CPP testing is performed through *gtest* immediately after building. To launch the CPP testing, run `./test-cpp.sh`:

.. literalinclude:: ../../../test-cpp.sh
  :language: bash

Please refer to *DRTLL SDK* for details.

#### Accelerating CPP testing

To skip SDK exporting (e.g. while debugging the test running), run:

```bash
./test-cpp.sh test
```

To skip both SDK exporting and checkpoint generation (e.g. while debugging the test building), run:

```bash
./test-cpp.sh test reuse-checkpoint
```

To use a sample config with shorter time for test data generation (a dummy training), run:

```bash
./test-cpp.sh fast test
```

TODO: refactor argument parsing logic in test scripts.

### Code Formatting

This project uses `black` for Python code formatting and `clang-format` for CXX code formatting:

.. literalinclude:: ../../../format-code.sh
  :language: bash

### Configuring vscode

`.vscode/settings.json`

```json
{
    "python.analysis.extraPaths": [
        "${workspaceFolder}/common/proto/proto_gen_py"
    ],
    "C_Cpp.default.includePath": [
        "${workspaceFolder}/common/proto/proto_gen_cpp"
    ]
}

```

### Debugging

Following global objects are useful for achieving runtime result consistency on the Python side and the C++ side:

- python: `common.io.GLOBAL_DEBUG_INFO`
- cpp: `drltt::global_debug_info`

For example, to compare runtime values of `rotation_radius_inv`, you may add two lines of code as follows than run `./test.sh fast`:

```diff
diff --git a/sdk/drltt-sdk/dynamics_models/bicycle_model.cpp b/sdk/drltt-sdk/dynamics_models/bicycle_model.cpp
index b694343..bcf01e4 100644
--- a/sdk/drltt-sdk/dynamics_models/bicycle_model.cpp
+++ b/sdk/drltt-sdk/dynamics_models/bicycle_model.cpp
@@ -96,6 +96,8 @@ bool BicycleModel::ComputeRotationRelatedVariables(
   *rotation_radius_inv =
       std::sin(*omega) / _hyper_parameter.bicycle_model().rearwheel_to_cog();
 
+  global_debug_info.add_data(*rotation_radius_inv);
+
   return true;
 }
 
diff --git a/simulator/dynamics_models/bicycle_model.py b/simulator/dynamics_models/bicycle_model.py
index a2df076..c93e8fe 100644
--- a/simulator/dynamics_models/bicycle_model.py
+++ b/simulator/dynamics_models/bicycle_model.py
@@ -180,6 +180,8 @@ class BicycleModel(BaseDynamicsModel):
         omega = normalize_angle(omega)
         rotation_radius_inv = np.sin(omega) / hyper_parameter.rearwheel_to_cog
 
+        from common import GLOBAL_DEBUG_INFO;GLOBAL_DEBUG_INFO.data.append(rotation_radius_inv)
+
         return omega, rotation_radius_inv
 
     @property
```

Check out log file to check the data. `gt_data` (ground-truth) denotes value on the Python side and `rt_data` (runtime) denotes value on the C++ side.

```text
5: Test case: 323, Step: 28
5:     gt_data: 0.000584156, rt_data: 0.000584146
5: Test case: 323, Step: 29
5:     gt_data: -8.38374e-05, rt_data: -8.38471e-05
5: Test case: 323, Step: 30
5:     gt_data: -0.00092932, rt_data: -0.00092933
5: Test case: 323, Step: 31
5:     gt_data: -0.00189424, rt_data: -0.00189425
```



## Citation

If you wish to cite this work, you may consider using the following reference form:

```text
Xu, Yinda, and Lidong Yu. "DRL-Based Trajectory Tracking for Motion-Related Modules in Autonomous Driving." arXiv preprint arXiv:2308.15991 (2023).
```
