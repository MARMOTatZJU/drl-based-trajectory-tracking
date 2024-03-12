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


if __name__ == '__main__':
    test_reference_line_manager()
