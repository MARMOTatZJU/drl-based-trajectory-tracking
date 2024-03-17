from typing import List, Tuple, Callable
from copy import deepcopy

import numpy as np
import gym

from simulator.environments.env_interface import ExtendedGymEnv


def roll_out_one_episode(
    environment: ExtendedGymEnv,
    policy_func: Callable,
    **kwargs,
) -> Tuple[List[np.ndarray], List[np.ndarray], List[np.ndarray]]:
    """Roll out one episode and return a trajectory.

    Args:
        environment: The associated environment.
        policy_func: The policy function, observation -> action.
    Returns:
        List[np.ndarray]: States.
        List[np.ndarray]: Actions.
        List[np.ndarray]: Observations.
    """
    states = list()
    actions = list()
    observations = list()

    obs = environment.reset(**kwargs)
    state = environment.get_state()

    done = False
    while not done:
        action = policy_func(obs)
        # collect data
        states.append(deepcopy(state))
        actions.append(deepcopy(action))
        observations.append(deepcopy(obs))
        # step environment
        obs, reward, done, info = environment.step(action)
        state = environment.get_state()

    return states, actions, observations
