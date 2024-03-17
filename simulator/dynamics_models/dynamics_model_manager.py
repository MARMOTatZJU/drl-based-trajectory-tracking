from typing import List, Tuple, Union, Iterable

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
    sampled_dynamics_model_index: int = -1

    def __init__(
        self, hyper_parameters: Iterable[HyperParameter] = tuple(), dynamics_model_configs: Iterable = tuple()
    ):
        """
        Args:
            dynamics_model_configs: configurations of dynamics models.
        """
        self.dynamics_models = list()
        self.sampled_dynamics_model = None

        if len(hyper_parameters) > 0:
            # TODO: add test for this branch
            for dynamics_hyper_parameter in hyper_parameters:
                dynamics_model_type = (
                    dynamics_hyper_parameter.type
                )  # TODO wrap this to function like build_object_within_registry_from_config
                dynamics_model = DYNAMICS_MODELS[dynamics_model_type](hyper_parameter=dynamics_hyper_parameter)
                self.dynamics_models.append(dynamics_model)
        else:
            for dynamics_model_config in dynamics_model_configs:
                dynamics_model = build_object_within_registry_from_config(DYNAMICS_MODELS, dynamics_model_config)
                self.dynamics_models.append(dynamics_model)

        # TODO: Check if all spaces are identical within the collection

        self.probabilities = (1 / len(self.dynamics_models),) * len(self.dynamics_models)
        self.sampled_dynamics_model = self.dynamics_models[0]

        # TODO: unify data structure for dynamics models
        self.names_to_indexes_and_dynamics_models = {
            dm.get_name(): (dm_idx, dm) for dm_idx, dm in enumerate(self.dynamics_models)
        }

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

    def get_dynamics_model_info(self) -> str:
        dm_infos = list()
        for dm in self.dynamics_models:
            dm_info = '\n'.join(
                (
                    dm.get_name(),
                    str(dm.hyper_parameter),
                )
            )
            dm_infos.append(dm_info)
        return '\n'.join(dm_infos)

    def select_dynamics_model_by_name(self, name: str) -> Tuple[int, BaseDynamicsModel]:
        return self.names_to_indexes_and_dynamics_models[name]

    def sample_dynamics_model(self) -> Tuple[int, BaseDynamicsModel]:
        """Randomly sample a dynamics model.

        Returns:
            BaseDynamicsModel: sampled dynamics model
        """
        self.sampled_dynamics_model_index = np.random.choice(range(len(self.dynamics_models)), p=self.probabilities)
        self.sampled_dynamics_model = self.dynamics_models[self.sampled_dynamics_model_index]
        return self.sampled_dynamics_model_index, self.get_sampled_dynamics_model()

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
