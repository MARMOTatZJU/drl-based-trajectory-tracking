import numpy as np

from simulator.dynamics_models import BicycleModel
from simulator.trajectory.random_walk import random_walk


def test_random_walk():
    dynamics_model = BicycleModel(
        front_overhang=0.9,
        rear_overhang=0.9,
        wheelbase=2.7,
        width=1.8,
        action_space_lb=[-3.0, -0.5235987755983],
        action_space_ub=[+3.0, +0.5235987755983],
    )
    dynamics_model.set_state(np.array((0.0, 0.0, 0.0, 10.0)))
    reference_line, trajectory = random_walk(dynamics_model, step_interval=0.1, walk_length=60)

    assert len(reference_line.waypoints) == 60
    assert len(trajectory.waypoints) == 60


if __name__ == '__main__':
    test_random_walk()
