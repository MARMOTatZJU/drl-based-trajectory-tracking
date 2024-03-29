import logging

logging.basicConfig(level=logging.INFO)

import numpy as np

DTYPE = np.float32
EPSILON = 1e-6

TEST_CONFIG_PATHS = (
    'configs/trajectory_tracking/config-track-base.yaml',
    'configs/trajectory_tracking/config-track-tiny.yaml',
    'configs/trajectory_tracking/test_samples/config-track-test-sample.yaml',
)

TEST_CHECKPOINT_DIR = 'work_dir/track-test/checkpoint'
