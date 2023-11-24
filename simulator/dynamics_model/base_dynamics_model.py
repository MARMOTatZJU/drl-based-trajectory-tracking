from typing import Union, Any
from abc import ABC, abstractmethod
from copy import deepcopy

import numpy as np
from gym.spaces import Space


DEFAULT_DTYPE = np.float32


class BaseDynamicsModel(ABC):
    """Base class for dynamics models

    Serve as definitions of dynamics/transition functions.

    Attributes:
        state: vectorized state of the dynamics model
        dtype: internal data type
    """

    state: np.ndarray
    dtype: np.dtype

    def __init__(
        self,
        init_state: np.ndarray = None,
        dtype: np.dtype = DEFAULT_DTYPE,
    ):
        if init_state is not None:
            self.set_state(init_state)
        self.set_dtype(dtype)

    def get_state(self) -> np.ndarray:
        return self.deserialize_state(self.state)

    def set_state(self, new_state: np.ndarray):
        self.state = self.serialize_state(new_state)

    def get_dtype(self) -> np.dtype:
        return self.dtype

    def set_dtype(self, dtype: np.dtype):
        self.dtype = dtype

    @classmethod
    @abstractmethod
    def serialize_state(cls, state: np.ndarray) -> Any:
        raise NotImplementedError

    @classmethod
    @abstractmethod
    def deserialize_state(cls, state: Any) -> np.ndarray:
        raise NotImplementedError

    @classmethod
    @abstractmethod
    def serialize_action(cls, action: np.ndarray) -> Any:
        raise NotImplementedError

    @classmethod
    @abstractmethod
    def deserialize_action(cls, action: Any) -> np.ndarray:
        raise NotImplementedError

    @abstractmethod
    def step(self, action: np.ndarray, delta_t: float):
        """Step the model's state forward by a specified time interval

        TODO: provide default implementation of `step` function (e.g. `step_without_update` + apply_delta_state)
        """
        raise NotImplementedError

    @abstractmethod
    def compute_next_state(self, action: np.ndarray, delta_t: float) -> Any:
        """
        Proceed a step forward by a specified time interval
            **without** update of internal state
        """
        raise NotImplementedError

    @abstractmethod
    def get_dynamics_model_observation(self) -> np.ndarray:
        """Make observation of the hyper-parameters of this dynamics model"""
        raise NotImplementedError

    @abstractmethod
    def get_state_observation(self) -> np.ndarray:
        """Make observation of the state of this dynamics model"""
        raise NotImplementedError

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
