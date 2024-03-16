
import numpy as np

from simulator import TEST_CHECKPOINT_DIR
from simulator.trajectory_tracker.trajectory_tracker import TrajectoryTracker



def test_trajectory_tracker_print():
    trajectory_tracker = TrajectoryTracker(checkpoint_dir=TEST_CHECKPOINT_DIR)
    trajectory_tracker.get_dynamics_model_info()


def test_trajectory_tracker_random_reference_line():
    trajectory_tracker = TrajectoryTracker(checkpoint_dir=TEST_CHECKPOINT_DIR)
    states, actions = trajectory_tracker.track_reference_line()
    assert len(states) == len(actions)


def test_trajectory_tracker():
    trajectory_tracker = TrajectoryTracker(checkpoint_dir=TEST_CHECKPOINT_DIR)

    init_v = 5.0
    init_r = 0.0
    init_state = (0.0, 0.0, init_r, init_v)
    tracking_length = 50
    step_interval = trajectory_tracker.get_step_interval()
    reference_line = [
        (
            np.cos(init_r) * init_v * step_interval * step_index,
            np.sin(init_r) * init_v * step_interval * step_index,
        )
        for step_index in range(tracking_length)
    ]
    states, actions = trajectory_tracker.track_reference_line(
        init_state=init_state,
        reference_line=reference_line,
    )

    assert len(states) == len(reference_line)
    assert len(actions) == len(reference_line)


if __name__ == '__main__':
   test_trajectory_tracker()
