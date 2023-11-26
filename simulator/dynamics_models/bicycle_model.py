from typing import Iterable, Any  # override
import math

import numpy as np
import gym
from gym.spaces import Space

from simulator import DTYPE
from . import BaseDynamicsModel
from common.geometry import normalize_angle

from proto_gen_py.dynamics_model.bicycle_model_pb2 import (
    BicycleModelHyperParameters,
    BicycleModelState,
    BicycleModelAction,
)


class BicycleModel(BaseDynamicsModel):
    """Bicycle model

    Suitable for vehicle/bicycle kinematics
    """

    hyper_parameters: BicycleModelHyperParameters
    state: BicycleModelState

    def __init__(
        self,
        front_overhang: float,
        wheelbase: float,
        rear_overhang: float,
        width: float,
        action_lb: Iterable[float] = (-math.inf, -math.inf),
        action_ub: Iterable[float] = (+math.inf, +math.inf),
        **kwargs,
    ):
        self.hyper_parameters = BicycleModelHyperParameters()
        self.hyper_parameters.front_overhang = front_overhang
        self.hyper_parameters.wheelbase = wheelbase
        self.hyper_parameters.rear_overhang = rear_overhang
        self.hyper_parameters.width = width
        length = front_overhang + wheelbase + rear_overhang
        self.hyper_parameters.length = length
        self.hyper_parameters.frontwheel_to_CoG = wheelbase + rear_overhang - length / 2
        self.hyper_parameters.rearwheel_to_CoG = wheelbase + front_overhang - length / 2
        self.hyper_parameters.action_ub.extend(action_ub)
        self.hyper_parameters.action_lb.extend(action_lb)

        self.state = BicycleModelState()

        super().__init__(**kwargs)

    @classmethod
    def serialize_state(cls, state: np.ndarray) -> Any:
        serialized_state = BicycleModelState()
        serialized_state.x = state[0]
        serialized_state.y = state[1]
        serialized_state.r = normalize_angle(state[2])
        serialized_state.v = state[3]

        return serialized_state

    @classmethod
    def deserialize_state(cls, state: Any) -> np.ndarray:
        deserialized_state = np.zeros((4,), dtype=DTYPE)
        deserialized_state[0] = state.x
        deserialized_state[1] = state.y
        deserialized_state[2] = state.r
        deserialized_state[3] = state.v

        return deserialized_state

    @classmethod
    def serialize_action(cls, action: np.ndarray) -> Any:
        serialized_action = BicycleModelAction()
        serialized_action.a = action[0]
        serialized_action.s = action[1]

        return serialized_action

    @classmethod
    def deserialize_action(cls, action: Any) -> np.ndarray:
        deserialized_action = np.zeros((2,), dtype=DTYPE)
        deserialized_action[0] = action.a
        deserialized_action[1] = action.s

        return deserialized_action

    def _compute_derivative(self, state: BicycleModelState, action: BicycleModelAction) -> BicycleModelState:
        x = state.x
        y = state.y
        r = state.r
        v = state.v
        a = action.a
        s = action.s

        gravity_center_relative_position = self.hyper_parameters.rearwheel_to_CoG / (
            self.hyper_parameters.rearwheel_to_CoG + self.hyper_parameters.frontwheel_to_CoG
        )
        omega = np.arctan(gravity_center_relative_position * np.tan(s))
        omega = normalize_angle(omega)

        dx_dt = v * np.cos(r + omega)
        dy_dt = v * np.sin(r + omega)
        dr_dt = v / self.hyper_parameters.rearwheel_to_CoG * np.sin(omega)
        dv_dt = a

        derivative = BicycleModelState()
        derivative.x = dx_dt
        derivative.y = dy_dt
        derivative.r = dr_dt
        derivative.v = dv_dt

        return derivative

    # @override
    def compute_next_state(self, action: np.ndarray, delta_t: float) -> Any:
        action = self.serialize_action(action)
        state_derivative = self._compute_derivative(self.state, action)
        next_state = self.serialize_state(
            self.deserialize_state(self.state) + self.deserialize_state(state_derivative) * delta_t
        )

        return next_state

    # @override
    def step(self, action: np.ndarray, delta_t: float):
        next_state = self.compute_next_state(action, delta_t)
        self.state = next_state

    # @override
    def get_dynamics_model_observation(self) -> np.ndarray:
        observation = np.array(
            (
                self.hyper_parameters.front_overhang,
                self.hyper_parameters.wheelbase,
                self.hyper_parameters.rear_overhang,
                self.hyper_parameters.width,
                self.hyper_parameters.length,
            ),
            dtype=DTYPE,
        )

        return observation

    # @override
    def get_state_observation(self) -> np.ndarray:
        observation = np.array((self.state.v,), dtype=DTYPE)

        return observation

    # @override
    def get_state_space(self) -> Space:
        state_space = gym.spaces.Box(
            low=np.array((-np.inf, -np.inf, -np.pi, 0.0), dtype=DTYPE),
            high=np.array((+np.inf, +np.inf, +np.pi, +np.inf), dtype=DTYPE),
            shape=(4,),
            dtype=self.get_dtype(),
        )

        return state_space

    # @override
    def get_action_space(self) -> Space:
        """Get action space"""
        lb = np.array(self.hyper_parameters.action_lb, dtype=DTYPE)
        ub = np.array(self.hyper_parameters.action_ub, dtype=DTYPE)
        action_space = gym.spaces.Box(
            low=lb,
            high=ub,
            shape=lb.shape,
            dtype=DTYPE,
        )

        return action_space

    # @override
    def jacobian(self, state: np.ndarray, action: np.ndarray) -> np.ndarray:
        pass
