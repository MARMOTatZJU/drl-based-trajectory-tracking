from typing import Tuple

from simulator.dynamics_models import BaseDynamicsModel

import numpy as np
import gym
from gym.spaces import Space


from drltt_proto.trajectory.trajectory_pb2 import ReferenceLineWaypoint, ReferenceLine, TrajectoryWaypoint, Trajectory


def random_walk(
    dynamics_model: BaseDynamicsModel,
    step_interval: float,
    walk_length: int,
) -> Tuple[ReferenceLine, Trajectory]:
    """Perform random walk to generate reference line"""
    assert walk_length >= 1, f'Illegal walk_length: {walk_length}'

    action_space: Space = dynamics_model.get_action_space()

    all_states = list()
    all_actions = list()
    for step_idx in range(walk_length - 1):
        state: np.ndarray = dynamics_model.get_state()
        action: np.ndarray = action_space.sample()

        all_states.append(state)
        all_actions.append(action)

        dynamics_model.step(action, step_interval)

    all_states.append(dynamics_model.get_state())
    all_actions.append(np.zeros_like(all_actions[-1]))

    reference_line = ReferenceLine()
    trajectory = Trajectory()
    for state, action in zip(all_states, all_actions):
        ref_wpt = ReferenceLineWaypoint()
        ref_wpt.x = state[0]
        ref_wpt.y = state[1]
        reference_line.waypoints.append(ref_wpt)

        trj_wpt = TrajectoryWaypoint()
        trj_wpt.state.CopyFrom(dynamics_model.serialize_state(state))
        trj_wpt.action.CopyFrom(dynamics_model.serialize_action(action))
        trajectory.waypoints.append(trj_wpt)

    return (reference_line, trajectory)
