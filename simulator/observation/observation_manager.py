import numpy as np
import gym

from drltt_proto.dynamics_model.basics_pb2 import BodyState
from simulator.dynamics_models import BaseDynamicsModel, DynamicsModelManager
from simulator.trajectory.reference_line import ReferenceLineManager


class ObservationManager:
    def __init__(
        self,
        reference_line_manager: ReferenceLineManager,
        dynamics_model_manager: DynamicsModelManager,
    ):
        self.reference_line_manager = reference_line_manager
        self.dynamics_model_manager = dynamics_model_manager

    def get_observation_space(
        self,
    ):
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

    def get_observation(self, index: int, body_state: BodyState):
        reference_line_observation = self.reference_line_manager.get_observation_by_index(index=index, body_state=body_state)
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
