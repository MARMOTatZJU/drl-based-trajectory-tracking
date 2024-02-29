# DRL-Based Trajectory Tracking (DRLTT)

This repo hosts code and script for training and deploying the *DRL-Based Trajectory Tracking (DRLTT)*  algorithm. DRLTT leverages Deep Reinforcement Learning (DRL) and achieves robustness, accuracy, and versatility in the Trajectory Tracking (TT) task. Benefiting from its methodological simplicity, DRLTT is able to process 32 trajectories (each contains 50 steps) within several milliseconds on edge computing devices.

Please refer to the [*Technical Report*](https://arxiv.org/abs/2308.15991) for details.

## Installation

- Python>=3.12
- `requirements/pypi.txt`

### Protobuf Compiler

```bash
source install-setup-protoc.sh
```

## RL Training & Evaluating

Setup a subfolder and create a `main.sh` with the following content, then execute it:

```bash
#!/bin/bash

source setup.sh
work_dir=$(dirname $0)
python scripts/train.py \
    --config-file configs/trajectory_tracking/config-tiny-track.yaml \
    --checkpoint-dir $work_dir/checkpoint/ \
    #
```

## Development

### System Design

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

### Formatting

This project uses `black` for Python code formatting and `clang-format` for CXX code formatting:

.. literalinclude:: ../../../format-code.sh
  :language: bash

## Testing

This project utilizes *pytest* for Python testing. To launch testing, run in command line:

```bash
pytest
```

CPP testing is performed through *gtest* immediately after building. Please refer to [./sdk/README.md](SDK-README for detail).


### Contribute to Documentation

This project adopts [Google-style Python docstrings](https://google.github.io/styleguide/pyguide.html), [Example Google Style Python Docstrings](https://sphinxcontrib-napoleon.readthedocs.io/en/latest/example_google.html) for auto-generation of API pages .

The authors would like to thank [PyTorch](https://pytorch.org/docs/stable/index.html) for being an exemplar of documentation.

#### For initialization

Initialize requirements of documentation generation:

```bash
pip install -r requirements/pypi-doc.txt
```

Initialize Sphinx project:

```bash
mkdir docs && cd docs
sphinx-quickstart
```

Build html:

```bash
cd build
make html
```

#### For incremental changes

As documentation of current project has already been set up, you can only run `make-html.sh` instead of previous steps:

.. literalinclude:: ../../../make-html.sh
  :language: bash


#### Start server and view documentation pages

Start http server on the remote side

```bash
cd build/html
python m http.server 8080 -b localhost
```

Create a ssh tunneling on the local side, which forward connections/requests from local to remote (server)

```bash
ssh -L 8080:localhost:8080 remote-server
```



### configure vscode

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

```
Xu, Yinda, and Lidong Yu. "DRL-Based Trajectory Tracking for Motion-Related Modules in Autonomous Driving." arXiv preprint arXiv:2308.15991 (2023).
```
