# DRL-Based Trajectory Tracking (DRLTT)

This repo hosts code and script for training and deploying the *DRL-Based Trajectory Tracking (DRLTT)*  algorithm. DRLTT leverages Deep Reinforcement Learning (DRL) and achieves robustness, accuracy, and versatility in the Trajectory Tracking (TT) task. Benefiting from its methodological simplicity, DRLTT is able to process 32 trajectories (each contains 50 steps) within several milliseconds on edge computing devices.

Please refer to the [*Technical Report*](https://arxiv.org/abs/2308.15991) for details.

## Installation

- Python>=3.12
- `requirements/pypi.txt`

### Protobuf Compiler

```
source install-steup-protoc.sh
```

## RL Training & Evaluating

Setup a subfolder and create a `main.sh` with the following content, then execute it:

```
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

```
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

This project uses `black` for code formatting.

```
black --config ./configs/code_formatting/pyproject.toml ./
```

## Testing

This project utilizes *pytest* for testing. To launch testing, run in command line:

```
pytest
```


### Contribute to Documentation

This project adopts [Google-style Python docstrings](https://google.github.io/styleguide/pyguide.html), [Example Google Style Python Docstrings](https://sphinxcontrib-napoleon.readthedocs.io/en/latest/example_google.html).

The authors would like to thank [PyTorch](https://pytorch.org/docs/stable/index.html) for being an exemplar of documentation.


```
pip install -r requirements/pypi-doc.txt
```

Initialize Sphinx project

```
mkdir docs && cd docs
sphinx-quickstart
```

Build html

```
cd build
make html
```

Start http server on the remote side

```
cd build/html
python m http.server 8080 -b localhost
```

Create a ssh tunneling on the local side, which forward connections/requests from local to remote (server)

```
ssh -L 8080:localhost:8080 remote-server
```



### configure vscode

`.vscode/settings.json`

```
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
