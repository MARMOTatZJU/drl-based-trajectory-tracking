# DRL-Based Trajectory Tracking

This repo hosts code and script for training and deploying *DRL-Based Trajectory Tracking* algorithm.

## Installation

- Python>=3.12
- `requirements/pypi.txt`

### Protobuf Compiler

```
source install-steup-protoc.sh
```

## RL training

Setup a subfolder and create a `train.sh` with follwoing content, then execute it:

```
#!/bin/bash
source setup.sh
work_dir=$(dirname $0)
python scripts/train.py \
    --config-file configs/trajectory_tracking/config-tiny-track.yaml \
    --checkpoint-file $work_dir/checkpoint.pkl \
    #
```

## Development

### System Design

- SB3-BaseAlgorithm
  - `TrajectoryTrackingEnv`
      - `ObservationManager`
          - `ReferenceLineManager`
          - `DynamicsModelManager`

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

The authors would like to thank [PyTorch](https://pytorch.org/docs/stable/index.html) for being an examplar of documentation.


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
