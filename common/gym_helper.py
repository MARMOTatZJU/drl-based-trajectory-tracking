import numpy as np

from gym.spaces import Space


def scale_action(action: np.ndarray, action_space: Space) -> np.ndarray:
    """Scale action into range [-1, +1]"""
    scaled_action = 2 * (action - action_space.low) / (action_space.high - action_space.low) - 1
    return scaled_action
