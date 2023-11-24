from typing import Union

import numpy as np


def normalize_angle(angle: Union[float, np.ndarray]) -> Union[float, np.ndarray]:
    """Normalize angle to [-pi, pi)

    Compatible with Numpy vectorization

    Args:
        angle: angle to be normalized

    Returns:
        normalized anlge

    """
    return (angle + np.pi) % (2 * np.pi) - np.pi
