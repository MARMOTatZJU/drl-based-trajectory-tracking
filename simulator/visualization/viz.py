from typing import Tuple

import matplotlib.pyplot as plt
import numpy as np
from jax import numpy as jnp

from waymax_viz.waymax.datatypes import Trajectory
from waymax_viz.waymax.visualization import (
    plot_trajectory,
    plot_trajectory,
    utils as viz_utils,
)

from drltt_proto.environment.trajectory_tracking_pb2 import TrajectoryTrackingEpisode


def visualize_trajectory_tracking_episode(
    episode: TrajectoryTrackingEpisode,
    viz_prefix: str,
    n_steps_per_viz: int = 10,
):
    """Visualize an episode of trajectory tracking and save images.

    TODO: fix non-unified data range issue.

    Args:
        episode (TrajectoryTrackingEpisode): Episode data of trajectory tracking.
        viz_prefix (str): The prefix of visualization files to be saved
        n_steps_per_viz (int, optional): Number of steps per draw. Defaults to 20.
    """
    traj_len = episode.tracking_length
    n_viz = traj_len // n_steps_per_viz

    for viz_idx in range(n_viz):
        viz_idx_range = (
            viz_idx * n_steps_per_viz,
            traj_len if viz_idx == n_viz - 1 else (viz_idx + 1) * n_steps_per_viz,
        )

        # shape=(#agents, #timesteps)
        traj = Trajectory(
            x=jnp.array([
                episode.dynamics_model.states[idx].bicycle_model.body_state.x for idx in range(*viz_idx_range)
            ]).reshape(1, -1),
            y=jnp.array([
                episode.dynamics_model.states[idx].bicycle_model.body_state.y for idx in range(*viz_idx_range)
            ]).reshape(1, -1),
            z=jnp.array([0.0 for idx in range(*viz_idx_range)]).reshape(1, -1),
            vel_x=jnp.array([
                np.cos(episode.dynamics_model.states[idx].bicycle_model.body_state.r)
                * episode.dynamics_model.states[idx].bicycle_model.v
                for idx in range(*viz_idx_range)
            ]).reshape(1, -1),
            vel_y=jnp.array([
                np.sin(episode.dynamics_model.states[idx].bicycle_model.body_state.r)
                * episode.dynamics_model.states[idx].bicycle_model.v
                for idx in range(*viz_idx_range)
            ]).reshape(1, -1),
            yaw=jnp.array([
                episode.dynamics_model.states[idx].bicycle_model.body_state.r for idx in range(*viz_idx_range)
            ]).reshape(1, -1),
            timestamp_micros=jnp.array(
                [int(episode.hyper_parameter.step_interval * 1e6 * idx) for idx in range(*viz_idx_range)],
                dtype=jnp.int32,
            ).reshape(1, -1),
            valid=jnp.array([True for idx in range(*viz_idx_range)], dtype=bool).reshape(1, -1),
            length=jnp.array([
                episode.dynamics_model.hyper_parameter.bicycle_model.length for idx in range(*viz_idx_range)
            ]).reshape(1, -1),
            width=jnp.array([
                episode.dynamics_model.hyper_parameter.bicycle_model.width for idx in range(*viz_idx_range)
            ]).reshape(1, -1),
            height=jnp.array([1.4 for idx in range(*viz_idx_range)]).reshape(1, -1),
        )
        n_steps_within_current_image = traj.shape[1]
        is_controlled = np.array([
            True,
        ]).reshape(
            1,
        )

        # determine axis limit
        fig, ax = viz_utils.init_fig_ax()
        ax.set_aspect('equal', adjustable='box')
        ax.set_box_aspect(1)
        for viz_step_idx in range(n_steps_within_current_image):
            plot_trajectory(ax, traj, is_controlled, time_idx=viz_step_idx)
        xy_lim = scale_xy_lim((ax.get_xlim(), ax.get_ylim()), ratio=1.3)
        stacked_img = viz_utils.img_from_fig(fig)
        viz_utils.save_img_as_png(stacked_img, f'{viz_prefix}-{viz_idx}-stacked.png')
        del fig, ax

        # TODO: figure out why manually stacking not work (probably related to detail of `plot_trajectory`)
        # all_imgs = list()
        # for viz_step_idx in range(n_steps_within_current_image):
        #     fig, ax = viz_utils.init_fig_ax()
        #     plot_trajectory(ax, traj, is_controlled, time_idx=viz_step_idx)
        #     # TODO: plot reference line
        #     ax.set_xlim(xy_lim[0])
        #     ax.set_ylim(xy_lim[1])
        #     ax.set_aspect('equal', adjustable='box')
        #     ax.set_box_aspect(1)
        #     img = viz_utils.img_from_fig(fig)
        #     all_imgs.append(img)
        # fused_image = np.stack(all_imgs, axis=0).mean(axis=0).astype(all_imgs[0].dtype)
        # # adjust intensity
        # for index in np.ndindex(fused_image.shape[:2]):
        #     intensity = get_subjective_brightness(fused_image[index])
        #     fused_image[index] = fused_image[index] * np.power(intensity, 4)
        # viz_utils.save_img_as_png(fused_image, f'{viz_prefix}-{viz_idx}.png')


def get_subjective_brightness(pixels: np.ndarray) -> np.ndarray:
    """_summary_
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
