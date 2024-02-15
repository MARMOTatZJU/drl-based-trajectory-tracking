# DRL-Based Trajectory Tracking

This repo hosts code and script for training and deploying *DRL-Based Trajectory Tracking* algorithm.

## Installation

- Python>=3.12
- `requirements/pypi.txt`

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
