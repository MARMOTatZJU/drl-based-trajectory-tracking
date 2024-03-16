from typing import Any
from abc import abstractmethod

import numpy as np
from gym import Env
from gym.spaces import Space

from drltt_proto.environment.environment_pb2 import Environment


class CustomizedEnvInterface:
    env_info: Environment

    @abstractmethod
    def export_environment_data(self) -> Any:
        raise NotImplementedError

    @abstractmethod
    def get_state(self) -> np.ndarray:
        raise NotImplementedError


class ExtendedGymEnv(Env, CustomizedEnvInterface):
    pass
