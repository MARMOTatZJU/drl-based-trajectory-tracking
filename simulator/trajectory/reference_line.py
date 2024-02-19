from typing import Iterable
import numpy as np
import gym
from gym.spaces import Space

from common.geometry import transform_to_local_from_world
from simulator import DTYPE
from drltt_proto.trajectory.trajectory_pb2 import ReferenceLine, ReferenceLineWaypoint
from drltt_proto.dynamics_model.basics_pb2 import BodyState


class ReferenceLineManager:
    """Manager for Reference Line.

    Attributes:
        reference_line: Handler of underlying reference line manager.
    """

    reference_line: ReferenceLine

    def __init__(self, n_observation_steps: int, dtype=DTYPE):
        """
        Args:
            n_observation_steps: Number of observation steps on the forward part of the reference line.
            dtype: Data type.
        """
        self.dtype = dtype
        self.n_observation_steps = n_observation_steps

    def set_reference_line(self, reference_line: ReferenceLine):
        """Set reference line.

        Args:
            reference_line: reference line to be set.
        """
        self.reference_line = reference_line

    def get_reference_line(self) -> ReferenceLine:
        """Return the underlygin reference line.

        Returns:
            ReferenceLine: Rreturned reference line
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
        obs_size = 2 * self.n_observation_steps
        observation_space = gym.spaces.Box(
            low=-(np.ones((obs_size,)) * np.inf).astype(dtype=DTYPE),
            high=+(np.ones((obs_size,)) * np.inf).astype(dtype=DTYPE),
            shape=(obs_size,),
            dtype=self.dtype,
        )
        return observation_space

    def get_observation_by_index(self, index: int, body_state: BodyState) -> np.ndarray:
        """Get vectorized observation of reference line given waypoint index.

        Args:
            index: Waypoint index.
            body_staate: Body state for ego-centric observation.

        Returns:
            np.ndarray: Vectorized reference line observation. Format: (x, y) x length.

        """
        if index + self.n_observation_steps >= len(self.reference_line.waypoints) + 1:
            raise ValueError(
                f'Getting observation from index {index} of length {self.n_observation_steps} will cause out-of-bound'
                f' error. The length of reference line is {len(self.reference_line.waypoints)}'
            )

        # TODO: move to `duplication` method for waypoints near the tail
        waypoint_list = list()
        for observed_waypoint in self.reference_line.waypoints[index : index + self.n_observation_steps]:
            waypoint = np.array(
                (
                    observed_waypoint.x,
                    observed_waypoint.y,
                )
            )
            waypoint_list.append(waypoint)
        all_waypoints = np.stack(waypoint_list, axis=0)  # (n_observation_steps, 2)

        # transform coordinate to body frame
        body_state_vec = np.array((body_state.x, body_state.y, body_state.r))
        all_waypoints_in_body_frame = transform_to_local_from_world(all_waypoints, body_state_vec)
        observation = all_waypoints_in_body_frame.reshape(-1)

        return observation

    def get_observation_by_state(self, body_state: BodyState, reference_line: ReferenceLine = None) -> np.ndarray:
        """TODO: to implement"""
        raise NotImplementedError

    def get_projected_waypoint_index(self, body_state: BodyState) -> np.ndarray:
        """TODO: to implement"""
        raise NotImplementedError
