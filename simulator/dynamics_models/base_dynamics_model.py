from abc import ABC, abstractmethod
from copy import deepcopy

import numpy as np
import gym
from gym.spaces import Space

from drltt_proto.dynamics_model.basics_pb2 import BodyState
from simulator import DTYPE

from drltt_proto.dynamics_model.hyper_parameter_pb2 import HyperParameter
from drltt_proto.dynamics_model.state_pb2 import State
from drltt_proto.dynamics_model.action_pb2 import Action


class BaseDynamicsModel(ABC):
    """Base class for dynamics models

    Serve as definitions of dynamics/transition functions.

    Attributes:
        state: vectorized state of the dynamics model
    """

    hyper_parameters: HyperParameter
    state: State

    def __init__(
        self,
        init_state: np.ndarray = None,
        **kwargs,
    ):
        if init_state is not None:
            self.set_state(init_state)

    def get_state(self) -> np.ndarray:
        return self.deserialize_state(self.state)

    def get_state_proto(self) -> np.ndarray:
        return self.state

    @abstractmethod
    def get_body_state_proto(self) -> BodyState:
        raise NotImplementedError

    def set_state(self, new_state: np.ndarray):
        self.state = self.serialize_state(new_state)

    @classmethod
    @abstractmethod
    def serialize_state(cls, state: np.ndarray) -> State:
        raise NotImplementedError

    @classmethod
    @abstractmethod
    def deserialize_state(cls, state: State) -> np.ndarray:
        raise NotImplementedError

    @classmethod
    @abstractmethod
    def serialize_action(cls, action: np.ndarray) -> Action:
        raise NotImplementedError

    @classmethod
    @abstractmethod
    def deserialize_action(cls, action: Action) -> np.ndarray:
        raise NotImplementedError

    def step(self, action: np.ndarray, delta_t: float):
        """Step the model's state forward by a specified time interval"""
        next_state = self.compute_next_state(action, delta_t)
        self.state = next_state

    @abstractmethod
    def compute_next_state(self, action: np.ndarray, delta_t: float) -> State:
        """
        Proceed a step forward by a specified time interval
            **without** update of internal state
        """
        raise NotImplementedError

    @abstractmethod
    def get_dynamics_model_observation(self) -> np.ndarray:
        """Make observation of the hyper-parameters of this dynamics model"""
        raise NotImplementedError

    def get_dynamics_model_observation_space(self) -> Space:
        observation = self.get_dynamics_model_observation()
        obs_size = observation.size
        space = gym.spaces.Box(
            low=-np.ones((obs_size,), dtype=DTYPE) * np.inf,
            high=+np.ones((obs_size,), dtype=DTYPE) * np.inf,
            shape=observation.shape,
            dtype=DTYPE,
        )

        return space

    @abstractmethod
    def get_state_observation(self) -> np.ndarray:
        """Make observation of the state of this dynamics model"""
        raise NotImplementedError

    def get_state_observation_space(self) -> Space:
        return self.get_state_space()

    @abstractmethod
    def get_state_space(self) -> Space:
        """Get state space"""
        raise NotImplementedError

    @abstractmethod
    def get_action_space(self) -> Space:
        """Get action space"""
        raise NotImplementedError

    @abstractmethod
    def jacobian(self, state: np.ndarray, action: np.ndarray) -> np.ndarray:
        """Compute jacobian with linearization

        Perform the linearzation at a given state-action pair

        Args:
            state: the state at the linearization point, shape=(n_dims_state,)
            action: the action at the linearization point, shape(n_dims_action,)

        Returns:
            jacobian matrix, shape=(n_dims_state, n_dims_state + n_dims_action)
        """
        raise NotImplementedError
