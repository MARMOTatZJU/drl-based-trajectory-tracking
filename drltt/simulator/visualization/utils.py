from typing import Tuple

import numpy as np


def get_subjective_brightness(pixels: np.ndarray) -> np.ndarray:
    """Get subjective brightness.
    Reference: https://computergraphics.stackexchange.com/questions/5085/light-intensity-of-an-rgb-value

    Args:
        pixels: Input pixels, shape=[..., 3], channel_order=<r, g, b>.

    Returns:
        np.ndarray: Brightness in [0.0, 1.0].
    """
    return np.round(0.21 * pixels[..., 0] + 0.72 * pixels[..., 1] + 0.07 * pixels[..., 2]) / 255.0


def scale_xy_lim(
    xy_lim: Tuple[Tuple[float, float], Tuple[float, float]], ratio: float
) -> Tuple[Tuple[float, float], Tuple[float, float]]:
    """Scale a pair of limits on x/y-axis with a scaling ratio.

    Args:
        xy_lim (Tuple[Tuple[float, float], Tuple[float, float]]): Limits on x/y-axis  to be scaled, format=<xlim, ylim>.
        ratio (float): Scaling ratio.

    Returns:
        Tuple[Tuple[float, float], Tuple[float, float]]: Scaled limits on x/y-axis.
    """
    x_lim, y_lim = xy_lim
    scaled_xlim = scale_axe_lim(x_lim, ratio)
    scaled_ylim = scale_axe_lim(y_lim, ratio)

    return (scaled_xlim, scaled_ylim)


def scale_axe_lim(axe_lim: Tuple[float, float], ratio: float) -> Tuple[float, float]:
    """Scale an axe limit.

    Args:
        axe_lim (Tuple[float, float]): Axe limit to be scaled.
        ratio (float): Scaling ratio.

    Returns:
        Tuple[float, float]: Scaled axe limit.
    """
    mid = (axe_lim[0] + axe_lim[1]) / 2
    scaled_lb = mid + (axe_lim[0] - mid) * ratio
    scaled_ub = mid + (axe_lim[1] - mid) * ratio

    return (scaled_lb, scaled_ub)
