import numpy as np
import gym
from gym.spaces import Space

from drltt_proto.dynamics_model.basics_pb2 import BodyState
from simulator.dynamics_models import BaseDynamicsModel, DynamicsModelManager
from simulator.trajectory.reference_line import ReferenceLineManager

from drltt_proto.environment.trajectory_tracking_pb2 import TrajectoryTrackingEpisode


class ObservationManager:
    """Manager for observation.

    Attributes:
        reference_line_manager: handler of underlying reference line manager
        dynamics_model_manager: handler of underlying Dynamics model manager
    """

    reference_line_manager: ReferenceLineManager
    dynamics_model_manager: DynamicsModelManager

    def __init__(
        self,
        reference_line_manager: ReferenceLineManager,
        dynamics_model_manager: DynamicsModelManager,
    ):
        """
        Args:
            reference_line_manager: Underlying reference line manager
            dynamics_model_manager: underlying Dynamics model manager
        """
        self.reference_line_manager = reference_line_manager
        self.dynamics_model_manager = dynamics_model_manager

    def get_observation_space(self) -> Space:
        """Return observation space, usually consisting of multiple sub-observation spaces.

        Returns:
            Space: observation space.
        """
        reference_line_observation_space = self.reference_line_manager.get_observation_space()
        state_observation_space = self.dynamics_model_manager.get_state_observation_space()
        synamics_model_observation_space = self.dynamics_model_manager.get_dynamics_model_observation_space()

        observation_space_tuple = gym.spaces.Tuple(
            (
                reference_line_observation_space,
                state_observation_space,
                synamics_model_observation_space,
            )
        )
        observation_space = gym.spaces.flatten_space(observation_space_tuple)

        return observation_space

    def get_observation(self, episode_data, body_state: BodyState) -> np.ndarray:
        """Return the vectorized observation, which is usually ego-centric.

        Args:
            episode_data: Episode data.
            body_state: (Serialized) body state of agent/dynamics model.

        Returns:
            np.ndarray: Vectorized observation.
        """
        reference_line_observation = self.reference_line_manager.get_observation_by_index(
            episode_data=episode_data, body_state=body_state
        )
        state_observation = self.dynamics_model_manager.get_sampled_dynamics_model().get_state_observation()
        dynamics_model_observation = (
            self.dynamics_model_manager.get_sampled_dynamics_model().get_dynamics_model_observation()
        )

        observation = np.concatenate(
            (
                reference_line_observation,
                state_observation,
                dynamics_model_observation,
            ),
            axis=0,
        )

        return observation
