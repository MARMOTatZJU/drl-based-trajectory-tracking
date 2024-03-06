from typing import List, Union, Iterable

import numpy as np
from gym.spaces import Space

from common import build_object_within_registry_from_config
from drltt_proto.dynamics_model.hyper_parameter_pb2 import HyperParameter
from . import BaseDynamicsModel, DYNAMICS_MODELS


class DynamicsModelManager:
    """Manager for Dynamics Models, suppporting random sampling/operating on sampled dyanmics model/etc.

    Attributes:
        dynamics_models: Collection of dynamics models
        sampled_dynamics_model: The currently sampled dynamics model.
    """

    dynamics_models: List[BaseDynamicsModel]
    sampled_dynamics_model: Union[BaseDynamicsModel, None] = None

    def __init__(self, dynamics_model_configs: Iterable = tuple()):
        """
        Args:
            dynamics_model_configs: configurations of dynamics models.
        """
        self.dynamics_models = list()
        self.sampled_dynamics_model = None
        for dynamics_model_config in dynamics_model_configs:
            dynamics_model = build_object_within_registry_from_config(DYNAMICS_MODELS, dynamics_model_config)
            self.dynamics_models.append(dynamics_model)

        # TODO: Check if all spaces are identical within the collection

        self.probabilities = (1 / len(self.dynamics_models),) * len(self.dynamics_models)
        self.sampled_dynamics_model = self.dynamics_models[0]

    def get_dynamics_model_observation_space(self) -> Space:
        """Get the dynamics model observation space. Assuming this space is identical across models within the collection

        Returns:
            Space: Dynamics model observation space.
        """
        return self.dynamics_models[0].get_dynamics_model_observation_space()

    def get_state_observation_space(self) -> Space:
        """Get the state observation space. Assuming this space is identical across models within the collection.

        Returns:
            Space: State observation space
        """
        return self.dynamics_models[0].get_state_observation_space()

    def sample_dynamics_model(self) -> BaseDynamicsModel:
        """Randomly sample a dynamics model.

        Returns:
            BaseDynamicsModel: sampled dynamics model
        """
        self.sampled_dynamics_model = np.random.choice(self.dynamics_models, p=self.probabilities)
        return self.get_sampled_dynamics_model()

    def get_sampled_dynamics_model(self) -> BaseDynamicsModel:
        """Return the sampled dynamics model.

        Returns:
            BaseDynamicsModel: Sampled dynamics model.
        """
        return self.sampled_dynamics_model

    def get_all_hyper_parameters(self) -> List[HyperParameter]:
        """TODO: docstring"""
        all_hyper_parameters = list()
        for dynamics_model in self.dynamics_models:
            hyper_parameter = HyperParameter()
            hyper_parameter.CopyFrom(dynamics_model.hyper_parameter)
            all_hyper_parameters.append(hyper_parameter)

        return all_hyper_parameters
