import numpy as np

from gym.spaces import Space


def scale_action(action: np.ndarray, action_space: Space) -> np.ndarray:
    """Scale action into range [-1, +1].

    Args:
        action: Action to be sclaled.
        action_space: Reference action space.

    Returns:
        np.ndarray: Scaled action.
    """
    scaled_action = 2 * (action - action_space.low) / (action_space.high - action_space.low) - 1
    return scaled_action
