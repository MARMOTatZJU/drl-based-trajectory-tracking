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

### Repository Cloning

This repo uses `git-submodule`. Run following command to clone:

```bash
git clone --recursive ${URL_TO_THIS_REPO}
```

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

## Try out Pre-trained Checkpoints

Pre-trained checkpoints and pre-compiled protobuf-generated code are collected in [drltt-assets](https://github.com/MARMOTatZJU/drltt-assets).

Set up environment variables by running:

```bash
source ./setup-minimum.sh
```

Then, launch a Python interpreter and run following code:

```python
import numpy as np
from simulator import TrajectoryTracker

pretrained_checkpoint_dir = './submodules/drltt-assets/checkpoints/track/checkpoint'
trajectory_tracker = TrajectoryTracker(checkpoint_dir=pretrained_checkpoint_dir)

states, actions = trajectory_tracker.track_reference_line()
reference_line = trajectory_tracker.get_reference_line()

print(f'States shape: {np.array(states).shape}')
print(f'Actions shape: {np.array(actions).shape}')
pos_diffs = np.array(reference_line) - np.array(states)[:, :2]
print('Position diff')
print(pos_diffs)
print(f'Position diff max.: {pos_diffs.max()}')
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


## Citation

If you wish to cite this work, you may consider using the following reference form:

```text
Xu, Yinda, and Lidong Yu. "DRL-Based Trajectory Tracking for Motion-Related Modules in Autonomous Driving." arXiv preprint arXiv:2308.15991 (2023).
```
