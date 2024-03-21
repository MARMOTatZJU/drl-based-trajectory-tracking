from typing import Any
from abc import abstractmethod

import numpy as np
from gym import Env
from gym.spaces import Space

from drltt_proto.environment.environment_pb2 import Environment


class CustomizedEnvInterface:
    """Customized interface for extending gym for DRLTT."""

    env_info: Environment

    @abstractmethod
    def export_environment_data(self) -> Environment:
        """Export environment data.

        Return:
            Environment: Environment data in proto structure.
        """
        env_data = Environment()
        env_data.CopyFrom(self.env_info)

        return env_data

    @abstractmethod
    def get_state(self) -> np.ndarray:
        """Get the underlying state.

        Returns:
            np.ndarray: Vectorized underlying state.
        """
        raise NotImplementedError


class ExtendedGymEnv(Env, CustomizedEnvInterface):
    """The type object for the extended gym environmnet."""

    pass
