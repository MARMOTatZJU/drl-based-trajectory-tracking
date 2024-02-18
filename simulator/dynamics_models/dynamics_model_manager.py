from typing import List, Union, Iterable
import numpy as np

from common import build_object_within_registry_from_config
from . import BaseDynamicsModel, DYNAMICS_MODELS


class DynamicsModelManager:
    dynamics_models: List[BaseDynamicsModel]
    sampled_dynamics_model: Union[BaseDynamicsModel, None] = None

    def __init__(self, dynamics_model_configs: Iterable = tuple()):
        self.dynamics_models = list()
        self.sampled_dynamics_model = None
        for dynamics_model_config in dynamics_model_configs:
            dynamics_model = build_object_within_registry_from_config(DYNAMICS_MODELS, dynamics_model_config)
            self.dynamics_models.append(dynamics_model)

        self.probabilities = (1 / len(self.dynamics_models),) * len(self.dynamics_models)
        self.sampled_dynamics_model = self.dynamics_models[0]

    def get_dynamics_model_observation_space(
        self,
    ):
        return self.dynamics_models[0].get_dynamics_model_observation_space()

    def get_state_observation_space(
        self,
    ):
        return self.dynamics_models[0].get_state_observation_space()

    def sample_dynamics_model(
        self,
    ) -> BaseDynamicsModel:
        self.sampled_dynamics_model = np.random.choice(self.dynamics_models, p=self.probabilities)
        return self.get_sampled_dynamics_model()

    def get_sampled_dynamics_model(
        self,
    ) -> BaseDynamicsModel:
        return self.sampled_dynamics_model
