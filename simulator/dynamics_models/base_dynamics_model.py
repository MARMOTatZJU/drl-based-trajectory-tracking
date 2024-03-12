from typing import Union
from abc import ABC, abstractmethod

import numpy as np
import gym
from gym.spaces import Space

from drltt_proto.dynamics_model.basics_pb2 import BodyState
from simulator import DTYPE

from drltt_proto.dynamics_model.hyper_parameter_pb2 import HyperParameter
from drltt_proto.dynamics_model.state_pb2 import State
from drltt_proto.dynamics_model.action_pb2 import Action
from drltt_proto.dynamics_model.observation_pb2 import Observation
from drltt_proto.dynamics_model.basics_pb2 import DebugInfo


class BaseDynamicsModel(ABC):
    """Base class for dynamics models defining state/action space, dynamics/transition functions, and more.

    Attributes:
        hyper_parameter: Hyper-parameter of the dynamics model.
        state: Vectorized state of the dynamics model.
    """

    hyper_parameter: HyperParameter
    state: State
    debug_info: DebugInfo

    def __init__(
        self,
        init_state: Union[np.ndarray, None] = None,
        **kwargs,
    ):
        """
        Args:
            init_state: Initial state to be set.
        """
        self.debug_info = DebugInfo()
        if init_state is not None:
            self.set_state(init_state)

    def get_state(self) -> np.ndarray:
        """Get the state in `np.ndarray` (deserialized form).

        Return:
            np.ndarray: Returned state.
        """
        return self.deserialize_state(self.state)

    def get_state_proto(self) -> State:
        """Get the state in proto (serialized form).

        Returns:
            State: State in proto.
        """
        return self.state

    @abstractmethod
    def get_body_state_proto(self) -> BodyState:
        """Return agent body's state in proto (serialized form).

        Return:
            BodyState: Body state of the dynamics model.
        """
        raise NotImplementedError

    def set_state(self, new_state: np.ndarray):
        self.state = self.serialize_state(new_state)

    @classmethod
    @abstractmethod
    def serialize_state(cls, state: np.ndarray) -> State:
        """Serialize state to proto.

        Args:
            state: Vectorized state.

        Returns:
            State: Serialized state.
        """
        raise NotImplementedError

    @classmethod
    @abstractmethod
    def deserialize_state(cls, state: State) -> np.ndarray:
        """Deserialize state to np.ndarray.

        Args:
            state: Serialized state.

        Returns:
            np.ndarray: Vectorized state.
        """
        raise NotImplementedError

    @classmethod
    @abstractmethod
    def serialize_action(cls, action: np.ndarray) -> Action:
        """Serialize action to proto.

        Args:
            action: Vectorized action.

        Returns:
            Action: Serialized action.
        """
        raise NotImplementedError

    @classmethod
    @abstractmethod
    def deserialize_action(cls, action: Action) -> np.ndarray:
        """Deserialize action to np.ndarray.

        Args:
            action: Serialized action.

        Returns:
            np.ndarray: Vectorized action.
        """
        raise NotImplementedError

    @classmethod
    @abstractmethod
    def serialize_observation(cls, observation: np.ndarray) -> Observation:
        raise NotImplementedError

    def step(self, action: np.ndarray, delta_t: float):
        """Step the model's state forward by a specified time interval.

        Args:
            action: Applied action.
            delta_t: Time interval.
        """
        self.debug_info.Clear()

        next_state = self.compute_next_state(action, delta_t)
        self.state = next_state

    @abstractmethod
    def compute_next_state(self, action: np.ndarray, delta_t: float) -> State:
        """Proceed a step forward by a specified time interval **without** update of internal state.

        Args:
            action: Applied vectorized action.
            delta_t: Time interval.
        """
        raise NotImplementedError

    @abstractmethod
    def get_dynamics_model_observation(self) -> np.ndarray:
        """Get dynamics model observationm usually containing hyper-parameter of the model.

        Returns:
            np.ndarray: Vectorized dynamics model observation.
        """
        raise NotImplementedError

    def get_dynamics_model_observation_space(self) -> Space:
        """Get dynamics model observation space where the dynamics model obervation lies in.

        Returns:
            Space: Dynamics model observation space.
        """
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
        """Return state observation of the dynamics model, which is usually body state-independent/ego centric.

        Returns:
            np.ndarray: Vectorised State observation.
        """
        raise NotImplementedError

    def get_state_observation_space(self) -> Space:
        """Get state observation space where the state observation lies in.

        Returns:
            Space: State obervstion space.
        """
        observation = self.get_state_observation()
        obs_size = observation.size
        space = gym.spaces.Box(
            low=-np.ones((obs_size,), dtype=DTYPE) * np.inf,
            high=+np.ones((obs_size,), dtype=DTYPE) * np.inf,
            shape=observation.shape,
            dtype=DTYPE,
        )

        return space

    @abstractmethod
    def get_state_space(self) -> Space:
        """Get state space.

        Returns:
            Space: State space.
        """
        raise NotImplementedError

    @abstractmethod
    def get_action_space(self) -> Space:
        """Get action space.

        Returns:
            Space: Action space.
        """
        raise NotImplementedError

    @abstractmethod
    def jacobian(self, state: np.ndarray, action: np.ndarray) -> np.ndarray:
        """Compute jacobian by performing linearization at a given point (state-action pair).

        Args:
            state: State at the linearization point, shape=(n_dims_state,).
            action: Action at the linearization point, shape(n_dims_action,).

        Returns:
            np.ndarray: Jacobian matrix, shape=(n_dims_state, n_dims_state + n_dims_action).
        """
        raise NotImplementedError

    def get_debug_info(self) -> DebugInfo:
        debug_info = DebugInfo()
        debug_info.CopyFrom(self.debug_info)

        return debug_info
