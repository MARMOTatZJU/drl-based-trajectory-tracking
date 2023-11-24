from typing import override
from copy import deepcopy

import numpy as np
import gym
from gym.spaces import Space

from . import BaseDynamicsModel
from common.geometry import normalize_angle

from proto_gen_py.dynamics_model.bicycle_model_pb2 import BicycleModelState, BicycleModelHyperParameters


class BicycleModel(BaseDynamicsModel):
    """Transition funciton

    State space:
        (x, y): position (in world frame)
        r: heading
        v: scalar velocity (at center of gravity)

    Action space:
        s: front wheel steer angle
        a: acceleration

    Convention of variable:
        delta_xxx: difference of variable xxx
        d_xxx: derivative of variable xxx w.r.t. time
    """

    hyper_parameters: BicycleModelHyperParameters
    state: BicycleModelState

    def __init__(
        self,
        front_overhang: float,
        wheelbase: float,
        rear_overhang: float,
        width: float,
        # ODE_method : str ='forward_euler',
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

        self.state = BicycleModelState()

        super().__init__(**kwargs)

    @classmethod
    def serialize_state(cls, state: np.ndarry) -> Any:
        serialized_state = BicycleModelState()
        serialized_state.x = state[0]
        serialized_state.y = state[1]
        serialized_state.r = normalize_angle(state[2])
        serialized_state.v = state[3]

        return serialized_state

    @classmethod
    def deserialize_state(cls, state: Any) -> np.ndarray:
        deserialized_state = np.zeros((4,), dtype=self.dtype)
        deserialized_state[0] = state.x
        deserialized_state[1] = state.y
        deserialized_state[2] = state.r
        deserialized_state[3] = state.v

        return deserialized_state

    @classmethod
    def serialize_action(cls, action: np.ndarry) -> Any:
        serialized_action = BicycleModelAction()
        serialized_action.a = action[0]
        serialized_action.s = action[1]

        return serialized_state

    @classmethod
    def deserialize_action(cls, action: Any) -> np.ndarray:
        deserialized_action = np.zeros((2,), dtype=self.dtype)
        deserialized_action[0] = action.a
        deserialized_action[1] = action.s

        return deserialized_action

    def _compute_derivative(self, state: BicycleModelState, action: BicycleModelAction) -> BicycleModelState:
        x = state.x
        y = state.y
        r = state.r
        v = state.v
        a = action.a
        a = action.s

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

    @override
    def compute_next_state(self, action: np.ndarray, delta_t: float) -> Any:
        action = self.serialize_action(action)
        state_dervative = self._compute_derivative(self.state, action)
        next_state = self.serialize_state(
            self.deserialize_state(self.state) + self.deserialize_state(state_derivative) * delta_t
        )

        return next_state

    @override
    def step(self, action: np.ndarray, delta_t: float):
        next_state = self.compute_next_state(action, delta_t)
        self.state = next_state

    @override
    def get_dynamics_model_observation(self) -> np.ndarray:
        observation = np.array(
            (
                self.hyper_parameters.front_overhang,
                self.hyper_parameters.wheelbase,
                self.hyper_parameters.rear_overhang,
                self.hyper_parameters.width,
                self.hyper_parameters.length,
            ),
            dtype=self.dtype,
        )

        return observation

    @override
    def get_state_observation(self) -> np.ndarray:
        observatoin = np.array((self.state.v,), dtype=self.dtype)

        return observation
