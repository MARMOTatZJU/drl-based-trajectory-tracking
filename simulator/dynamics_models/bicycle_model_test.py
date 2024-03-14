import numpy as np

from simulator.dynamics_models import BicycleModel


def test_bicycle_model():
    dynamics_model = BicycleModel(
        front_overhang=0.9,
        rear_overhang=0.9,
        wheelbase=2.7,
        width=1.8,
        action_space_lb=[-3.0, -0.5235987755983],
        action_space_ub=[+3.0, +0.5235987755983],
        max_lat_acc=2.0,
    )
    dynamics_model.set_state(np.array((0.0, 0.0, 0.0, 5.0)))
    assert dynamics_model.cog_relative_position_between_axles > 0.0
    assert dynamics_model.cog_relative_position_between_axles < 1.0
    assert dynamics_model.max_steer > 0.0
    assert dynamics_model.max_steer < np.pi


if __name__ == '__main__':
    test_bicycle_model()
