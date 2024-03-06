from typing import Dict, Iterable, Union, Any, override
import math
from copy import deepcopy

import numpy as np
import gym
from gym.spaces import Space

from simulator import DTYPE
from . import BaseDynamicsModel, DYNAMICS_MODELS
from common.geometry import normalize_angle

from drltt_proto.dynamics_model.hyper_parameter_pb2 import HyperParameter, BicycleModelHyperParameter
from drltt_proto.dynamics_model.state_pb2 import State
from drltt_proto.dynamics_model.action_pb2 import Action
from drltt_proto.dynamics_model.observation_pb2 import Observation


@DYNAMICS_MODELS.register
class BicycleModel(BaseDynamicsModel):
    """Bicycle model, suitable for modeling vehicle/bicycle kinematics."""

    def __init__(
        self,
        hyper_parameter: Union[HyperParameter, None] = None,
        **kwargs,
    ):
        """
        Args:
            hyper_parameters: hyper parameter of bicylce model
                if protobuf-typed hyper-parameters is not provided, then parse arguments from kwargs.
                if protobuf-typed hyper-parameters are provided, then assign them to the underlying `hyper_hyperparameters`.
        """
        self.hyper_parameter = HyperParameter()
        if hyper_parameter is None:
            # parse from key-word arguments
            self.parse_hyper_parameter(self.hyper_parameter, **kwargs)
        else:
            # set parsed hyper-parameter
            self.hyper_parameter = deepcopy(hyper_parameter)

        self.state = State()

        super().__init__(**kwargs)

    @classmethod
    def parse_hyper_parameter(
        cls,
        hyper_parameter: HyperParameter = None,
        front_overhang: float = 0.0,
        wheelbase: float = 0.0,
        rear_overhang: float = 0.0,
        width: float = 0.0,
        action_space_lb: Iterable[float] = (-math.inf, -math.inf),
        action_space_ub: Iterable[float] = (+math.inf, +math.inf),
        **kwargs,
    ):
        """
        Args:
            hyper_parameter: Hyper-parameter as parsing result.
            front_overhang: Distance from front axle to vehicle front.
            wheelbase: Distance between front axle and rear axle.
            rear_overhang: Distance from rear axle to vehicle rear.
            width: Width of vehicle.
            action_space_lb: lower bound of action space.
            action_space_ub: upper bound of action space.
        """
        hyper_parameter.type = cls.__name__
        hyper_parameter.bicycle_model.front_overhang = front_overhang
        hyper_parameter.bicycle_model.wheelbase = wheelbase
        hyper_parameter.bicycle_model.rear_overhang = rear_overhang
        hyper_parameter.bicycle_model.width = width
        length = front_overhang + wheelbase + rear_overhang
        hyper_parameter.bicycle_model.length = length
        hyper_parameter.bicycle_model.frontwheel_to_cog = wheelbase + rear_overhang - length / 2
        hyper_parameter.bicycle_model.rearwheel_to_cog = wheelbase + front_overhang - length / 2
        hyper_parameter.bicycle_model.action_space_ub.extend(action_space_ub)
        hyper_parameter.bicycle_model.action_space_lb.extend(action_space_lb)

    @classmethod
    @override
    def serialize_state(cls, state: np.ndarray) -> State:
        serialized_state = State()
        serialized_state.bicycle_model.body_state.x = state[0]
        serialized_state.bicycle_model.body_state.y = state[1]
        serialized_state.bicycle_model.body_state.r = normalize_angle(state[2])
        serialized_state.bicycle_model.v = state[3]

        return serialized_state

    @classmethod
    @override
    def deserialize_state(cls, state: State) -> np.ndarray:
        deserialized_state = np.zeros((4,), dtype=DTYPE)
        deserialized_state[0] = state.bicycle_model.body_state.x
        deserialized_state[1] = state.bicycle_model.body_state.y
        deserialized_state[2] = state.bicycle_model.body_state.r
        deserialized_state[3] = state.bicycle_model.v

        return deserialized_state

    @override
    def get_body_state_proto(self):
        return self.state.bicycle_model.body_state

    @classmethod
    @override
    def serialize_action(cls, action: np.ndarray) -> Action:
        serialized_action = Action()
        serialized_action.bicycle_model.a = action[0]
        serialized_action.bicycle_model.s = action[1]

        return serialized_action

    @classmethod
    @override
    def deserialize_action(cls, action: Action) -> np.ndarray:
        deserialized_action = np.zeros((2,), dtype=DTYPE)
        deserialized_action[0] = action.bicycle_model.a
        deserialized_action[1] = action.bicycle_model.s

        return deserialized_action

    @classmethod
    @override
    def serialize_observation(cls, observation: np.ndarray) -> Observation:
        serialized_observation = Observation()
        serialized_observation.bicycle_model.feature.extend(observation)

        return serialized_observation

    def _compute_derivative(self, state: State, action: Action) -> State:
        hyper_parameter = self.hyper_parameter.bicycle_model

        x = state.bicycle_model.body_state.x
        y = state.bicycle_model.body_state.y
        r = state.bicycle_model.body_state.r
        v = state.bicycle_model.v
        a = action.bicycle_model.a
        s = action.bicycle_model.s

        gravity_center_relative_position = hyper_parameter.rearwheel_to_cog / (
            hyper_parameter.rearwheel_to_cog + hyper_parameter.frontwheel_to_cog
        )
        omega = np.arctan(gravity_center_relative_position * np.tan(s))
        omega = normalize_angle(omega)

        dx_dt = v * np.cos(r + omega)
        dy_dt = v * np.sin(r + omega)
        dr_dt = v / hyper_parameter.rearwheel_to_cog * np.sin(omega)
        dv_dt = a

        derivative = State()
        derivative.bicycle_model.body_state.x = dx_dt
        derivative.bicycle_model.body_state.y = dy_dt
        derivative.bicycle_model.body_state.r = dr_dt
        derivative.bicycle_model.v = dv_dt

        return derivative

    @override
    def compute_next_state(self, action: np.ndarray, delta_t: float) -> Any:
        action = self.serialize_action(action)
        state_derivative = self._compute_derivative(self.state, action)
        next_state = self.serialize_state(
            self.deserialize_state(self.state) + self.deserialize_state(state_derivative) * delta_t
        )

        return next_state

    @override
    def get_dynamics_model_observation(self) -> np.ndarray:
        hyper_parameter = self.hyper_parameter.bicycle_model
        observation = np.array(
            (
                hyper_parameter.front_overhang,
                hyper_parameter.wheelbase,
                hyper_parameter.rear_overhang,
                hyper_parameter.width,
                hyper_parameter.length,
            ),
            dtype=DTYPE,
        )

        return observation

    @override
    def get_state_observation(self) -> np.ndarray:
        observation = np.array((self.state.bicycle_model.v,), dtype=DTYPE)

        return observation

    @override
    def get_state_observation_space(self) -> Space:
        state_observation_space = gym.spaces.Box(
            low=np.array((0.0,), dtype=DTYPE),
            high=np.array((+np.inf,), dtype=DTYPE),
            shape=(1,),
            dtype=DTYPE,
        )
        return state_observation_space

    @override
    def get_state_space(self) -> Space:
        state_space = gym.spaces.Box(
            low=np.array((-np.inf, -np.inf, -np.pi, 0.0), dtype=DTYPE),
            high=np.array((+np.inf, +np.inf, +np.pi, +np.inf), dtype=DTYPE),
            shape=(4,),
            dtype=DTYPE,
        )

        return state_space

    @override
    def get_action_space(self) -> Space:
        """Get action space"""
        hyper_parameter = self.hyper_parameter.bicycle_model
        lb = np.array(hyper_parameter.action_space_lb, dtype=DTYPE)
        ub = np.array(hyper_parameter.action_space_ub, dtype=DTYPE)
        assert lb.shape == ub.shape, (
            f'In `hyper_parameters`, action_space_lb\'s shape {lb.shape} does not match action_space_ub\'s shape'
            f' {ub.shape}'
        )
        action_space = gym.spaces.Box(
            low=lb,
            high=ub,
            shape=lb.shape,
            dtype=DTYPE,
        )

        return action_space

    @override
    def jacobian(self, state: np.ndarray, action: np.ndarray) -> np.ndarray:
        raise NotImplementedError
