import math

import matplotlib
import numpy as np
from jax import numpy as jnp

from waymax_viz.waymax import datatypes
from waymax_viz.waymax.datatypes import Trajectory, RoadgraphPoints, MapElementIds
from waymax_viz.waymax.visualization import (
    plot_trajectory,
    utils as viz_utils,
    color,
)
from waymax_viz.waymax.visualization.viz import (
    _RoadGraphShown,
    _RoadGraphDefaultColor,
)


from drltt_proto.environment.environment_pb2 import Environment
from simulator.visualization import VISUALIZATION_FUNCTIONS

from .utils import scale_xy_lim


@VISUALIZATION_FUNCTIONS.register
def visualize_trajectory_tracking_episode(
    env_data: Environment,
    viz_prefix: str,
    n_steps_per_viz: int = 30,
):
    """Visualize an episode of trajectory tracking and save images.

    TODO: fix non-unified data range issue.

    Args:
        episode (TrajectoryTrackingEpisode): Episode data of trajectory tracking.
        viz_prefix (str): The prefix of visualization files to be saved.
        n_steps_per_viz (int, optional): Number of steps per draw. Defaults to 20.
    """
    assert isinstance(env_data, Environment), f'`visualize_trajectory_tracking_episode` requires env_data to be in class `Environment`'
    episode = env_data.trajectory_tracking.episode

    traj_len = episode.tracking_length
    n_viz = traj_len // n_steps_per_viz

    for viz_idx in range(n_viz):
        viz_idx_range = (
            viz_idx * n_steps_per_viz,
            traj_len if viz_idx == n_viz - 1 else (viz_idx + 1) * n_steps_per_viz,
        )

        # plot trajectory
        dm_states = episode.dynamics_model.states
        traj = Trajectory(
            x=jnp.array([dm_states[idx].bicycle_model.body_state.x for idx in range(*viz_idx_range)]).reshape(1, -1),
            y=jnp.array([dm_states[idx].bicycle_model.body_state.y for idx in range(*viz_idx_range)]).reshape(1, -1),
            z=jnp.array([0.0 for idx in range(*viz_idx_range)]).reshape(1, -1),
            vel_x=jnp.array([
                np.cos(dm_states[idx].bicycle_model.body_state.r) * dm_states[idx].bicycle_model.v
                for idx in range(*viz_idx_range)
            ]).reshape(1, -1),
            vel_y=jnp.array([
                np.sin(dm_states[idx].bicycle_model.body_state.r) * dm_states[idx].bicycle_model.v
                for idx in range(*viz_idx_range)
            ]).reshape(1, -1),
            yaw=jnp.array([dm_states[idx].bicycle_model.body_state.r for idx in range(*viz_idx_range)]).reshape(1, -1),
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
        )  # shape=(#agents, #timesteps)
        refline_waypoints = episode.reference_line.waypoints
        reference_line = RoadgraphPoints(
            x=jnp.array([refline_waypoints[idx].x for idx in range(*viz_idx_range)]).reshape(-1),
            y=jnp.array([refline_waypoints[idx].y for idx in range(*viz_idx_range)]).reshape(-1),
            z=jnp.array([0.0 for idx in range(*viz_idx_range)]).reshape(-1),
            dir_x=jnp.array([
                refline_waypoints[idx].x / math.hypot(refline_waypoints[idx].x, refline_waypoints[idx].y)
                for idx in range(*viz_idx_range)
            ]).reshape(-1),
            dir_y=jnp.array([
                refline_waypoints[idx].y / math.hypot(refline_waypoints[idx].x, refline_waypoints[idx].y)
                for idx in range(*viz_idx_range)
            ]).reshape(-1),
            dir_z=jnp.array([0.0 for idx in range(*viz_idx_range)]).reshape(-1),
            types=jnp.array([MapElementIds.STOP_SIGN for idx in range(*viz_idx_range)], dtype=np.int32).reshape(-1),
            ids=jnp.array([idx for idx in range(*viz_idx_range)], dtype=np.int32).reshape(-1),
            valid=jnp.array([True for idx in range(*viz_idx_range)], dtype=bool).reshape(-1),
        )  # shape=(#timesteps)
        n_steps_within_current_image = traj.shape[1]
        is_controlled = np.array([
            True,
        ]).reshape(1)
        fig, ax = viz_utils.init_fig_ax()
        ax.set_aspect('equal', adjustable='box')
        ax.set_box_aspect(1)
        for viz_step_idx in range(n_steps_within_current_image):
            plot_trajectory(ax, traj, is_controlled, time_idx=viz_step_idx)
        plot_roadgraph_points(ax, reference_line)
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


# fmt: off
def plot_roadgraph_points(
    ax: matplotlib.axes.Axes,
    rg_pts: datatypes.RoadgraphPoints,
    verbose: bool = False,
) -> None:
  """Overwritten function from Waymax.

  Modified items:
  - line type.
  - overlap level (zorder)
  """
  if len(rg_pts.shape) != 1:
    raise ValueError(f'Roadgraph should be rank 1, got {len(rg_pts.shape)}')
  if rg_pts.valid.sum() == 0:
    return
  elif verbose:
    print(f'Roadgraph points count: {rg_pts.valid.sum()}')

  xy = rg_pts.xy[rg_pts.valid]
  rg_type = rg_pts.types[rg_pts.valid]
  for curr_type in np.unique(rg_type):
    if curr_type in _RoadGraphShown:
      p1 = xy[rg_type == curr_type]
      rg_color = color.ROAD_GRAPH_COLORS.get(curr_type, _RoadGraphDefaultColor)
      ax.plot(p1[:, 0], p1[:, 1], 'o-', color=rg_color, ms=3, zorder=15)
# fmt: on
