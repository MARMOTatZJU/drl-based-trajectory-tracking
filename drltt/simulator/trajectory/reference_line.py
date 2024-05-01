import numpy as np
import gym
from gym.spaces import Space

from drltt.common.geometry import transform_to_local_from_world
from drltt.simulator import DTYPE

from drltt_proto.trajectory.trajectory_pb2 import ReferenceLine, ReferenceLineWaypoint
from drltt_proto.dynamics_model.basics_pb2 import BodyState
from drltt_proto.dynamics_model.state_pb2 import State
from drltt_proto.environment.trajectory_tracking_pb2 import TrajectoryTrackingEpisode


class ReferenceLineManager:
    """Manager for Reference Line.

    Attributes:
        reference_line: Handler of underlying reference line manager.
        pad_mode: Mode used for reference line padding.
        dtype: Data type for reference line representation and observation

    """

    reference_line: ReferenceLine
    raw_reference_line: ReferenceLine
    pad_mode: str
    dtype: np.dtype

    def __init__(
        self,
        n_observation_steps: int,
        pad_mode: str = 'none',
        dtype: np.dtype = DTYPE,
    ):
        """
        Args:
            n_observation_steps: Number of observation steps on the forward part of the reference line.
            pad_mode: Desired mode used for reference line padding.
            dtype: Desired data type.
        """
        self.n_observation_steps = n_observation_steps
        self.pad_mode = pad_mode
        self.dtype = dtype

    def set_reference_line(
        self,
        reference_line: ReferenceLine,
        tracking_length: int = 0,
    ):
        """Set reference line.

        Args:
            reference_line: Reference line to be set.
            tracking_length: Desired tracking length of reference line.
        """
        self.raw_reference_line = ReferenceLine()
        self.raw_reference_line.CopyFrom(reference_line)

        self.reference_line = ReferenceLine()
        self.reference_line.CopyFrom(reference_line)

        if tracking_length <= 0:
            tracking_length = len(self.reference_line.waypoints)

        # padding
        # (tracking_length + n_observation_steps) is required as the last observation need to be returned at waypoints[tracking_length]
        if self.pad_mode == 'none':
            pass
        elif self.pad_mode == 'repeat':
            del self.reference_line.waypoints[tracking_length:]  # remove last `n_observation_steps` padded elements
            n_repeat = self.n_observation_steps
            last_waypoint = self.reference_line.waypoints[-1]
            for _ in range(n_repeat):
                repeated_waypoint = ReferenceLineWaypoint()
                repeated_waypoint.CopyFrom(last_waypoint)
                self.reference_line.waypoints.append(last_waypoint)
        else:
            raise ValueError(f'Unknown `pad_mode`: {self.pad_mode}')

    def get_reference_line(self) -> ReferenceLine:
        """Return the underlying reference line.

        Returns:
            ReferenceLine: Returned reference line
        """
        return self.reference_line

    def get_reference_line_waypoint(self, index: int) -> np.ndarray:
        """Get a waypoint on the reference line.

        Args:
            index: Step index of the desired waypoint.

        Returns:
            np.ndarray: Reference line waypoint (vectorized form).
        """
        waypoint = np.array(
            (
                self.reference_line.waypoints[index].x,
                self.reference_line.waypoints[index].y,
            ),
            dtype=DTYPE,
        )

        return waypoint

    def get_observation_space(self) -> Space:
        """Get observation space.

        Returns:
            Space: Observation space.
        """
        obs_size = 2 * self.n_observation_steps + 1  # consider an automatic way. e.g. define an default reference line
        observation_space = gym.spaces.Box(
            low=-(np.ones((obs_size,)) * np.inf).astype(dtype=DTYPE),
            high=+(np.ones((obs_size,)) * np.inf).astype(dtype=DTYPE),
            shape=(obs_size,),
            dtype=self.dtype,
        )
        return observation_space

    def get_observation_by_index(self, episode_data, body_state: BodyState) -> np.ndarray:
        """Get vectorized observation of reference line given waypoint index.

        Args:
            episode_data: Episode data.
            body_state: Body state for ego-centric observation.

        Returns:
            np.ndarray: Vectorized reference line observation. Format: (x, y) x length.

        """
        # TODO: resolve hardcode
        index = episode_data.step_index
        tracking_length = episode_data.tracking_length
        forward_tracking_length = tracking_length - index

        if index + self.n_observation_steps >= len(self.reference_line.waypoints) + 1:
            raise ValueError(
                f'Getting observation from index {index} of length {self.n_observation_steps} will cause out-of-bound'
                f' error. The length of reference line is {len(self.reference_line.waypoints)}'
            )

        waypoint_list = list()
        for observed_waypoint in self.reference_line.waypoints[index : index + self.n_observation_steps]:
            waypoint = np.array(
                (
                    observed_waypoint.x,
                    observed_waypoint.y,
                ),
                dtype=DTYPE,
            )
            waypoint_list.append(waypoint)
        all_waypoints = np.stack(waypoint_list, axis=0)  # (n_observation_steps, 2)

        # transform coordinate to body frame
        body_state_vec = np.array((body_state.x, body_state.y, body_state.r))
        all_waypoints_in_body_frame = transform_to_local_from_world(all_waypoints, body_state_vec)
        observation = all_waypoints_in_body_frame.reshape(-1)

        observation = np.concatenate(
            (
                observation,
                np.array((forward_tracking_length,), dtype=DTYPE),
            )
        ).reshape(-1)

        return observation

    def get_observation_by_state(self, body_state: BodyState, reference_line: ReferenceLine = None) -> np.ndarray:
        """TODO: to implement"""
        raise NotImplementedError

    def get_projected_waypoint_index(self, body_state: BodyState) -> np.ndarray:
        """TODO: to implement"""
        raise NotImplementedError

    @classmethod
    def np_array_to_reference_line(cls, arr: np.ndarray) -> ReferenceLine:
        assert arr.ndim == 2
        assert arr.shape[1] == 2
        reference_line = ReferenceLine()
        for np_pt in arr:
            waypoint = ReferenceLineWaypoint(
                x=np_pt[0],
                y=np_pt[1],
            )
            reference_line.waypoints.append(waypoint)

        return reference_line

    @classmethod
    def reference_line_to_np_array(cls, reference_line: ReferenceLine) -> np.ndarray:
        waypoints = list()
        for waypoint in reference_line.waypoints:
            waypoints.append(np.array((waypoint.x, waypoint.y)))

        waypoints = np.stack(waypoints, axis=0)

        return waypoints

    @classmethod
    def estimate_init_state_from_reference_line(
        cls, reference_line: ReferenceLine, delta_t: float, window_size: int = 5
    ) -> State:
        length = len(reference_line.waypoints)
        if length < 1:
            raise ValueError(f'Reference line\'s length is too short: {length}')

        discount_factor = 1 / np.exp(1.0)
        real_window_size = min(window_size, length)
        window_refline = cls.reference_line_to_np_array(reference_line)[:real_window_size]  # (N-1, 2)
        window_refline_diffs = window_refline[1:] - window_refline[:-1]  # (N-1, 2)
        window_refline_disps = np.linalg.norm(window_refline_diffs, axis=1).reshape(-1, 1)  # (N-1, 1)
        weights = np.power(discount_factor, np.arange(real_window_size - 1)).reshape(-1, 1)  # (N-1, 1)

        estimated_v = (window_refline_disps * weights).sum() / weights.sum() / delta_t  # (1,)
        estimated_diff = (window_refline_diffs * weights).sum(axis=0) / weights.sum()  # (2,)
        estimated_r = np.arctan2(estimated_diff[1], estimated_diff[0])  # (1,)

        estimated_init_state = State()
        estimated_init_state.bicycle_model.body_state.x = window_refline[0][0]
        estimated_init_state.bicycle_model.body_state.y = window_refline[0][1]
        estimated_init_state.bicycle_model.body_state.r = estimated_r
        estimated_init_state.bicycle_model.v = estimated_v

        return estimated_init_state
