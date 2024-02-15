# DRL-Based Trajectory Tracking

This repo hosts code and script for training and deploying *DRL-Based Trajectory Tracking* algorithm.

## Installation

- Python>=3.12
- `requirements/pypi.txt`

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
