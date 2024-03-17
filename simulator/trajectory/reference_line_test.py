import numpy as np

from simulator.dynamics_models import BicycleModel
from simulator.trajectory.random_walk import random_walk
from simulator.trajectory.reference_line import ReferenceLineManager


def test_reference_line_manager():
    dynamics_model = BicycleModel(
        front_overhang=0.9,
        rear_overhang=0.9,
        wheelbase=2.7,
        width=1.8,
        action_space_lb=[-3.0, -0.5235987755983],
        action_space_ub=[+3.0, +0.5235987755983],
    )
    dynamics_model.set_state(np.array((0.0, 0.0, 0.0, 10.0)))
    tracking_length = 60
    n_observation_steps = 15
    reference_line, trajectory = random_walk(dynamics_model, step_interval=0.1, walk_length=tracking_length)
    reference_line_manager = ReferenceLineManager(
        n_observation_steps=n_observation_steps,
        pad_mode='repeat',
    )
    reference_line_manager.set_reference_line(reference_line, tracking_length=tracking_length)
    assert len(reference_line_manager.raw_reference_line.waypoints) == 60


def test_estimate_init_state_from_reference_line():
    step_interval = 0.1
    init_v = 5.0
    init_r = np.pi / 3
    reference_line_length = 20

    reference_line_arr = np.array([
        (
            np.cos(init_r) * init_v * step_interval * step_index,
            np.sin(init_r) * init_v * step_interval * step_index,
        )
        for step_index in range(reference_line_length)
    ])
    reference_line = ReferenceLineManager.np_array_to_reference_line(reference_line_arr)
    estimated_init_state = ReferenceLineManager.estimate_init_state_from_reference_line(reference_line, step_interval)
    assert np.isclose(estimated_init_state.bicycle_model.body_state.r, init_r)
    assert np.isclose(estimated_init_state.bicycle_model.v, init_v)


if __name__ == '__main__':
    test_reference_line_manager()
    test_estimate_init_state_from_reference_line()
