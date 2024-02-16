from typing import List, Tuple, Dict, Union, Any, Optional, Generator, override
import os
import math
from copy import deepcopy
import random

import numpy as np
import gym
from gym.spaces import Space

from . import ENVIRONMENTS
from simulator import DTYPE
from simulator.dynamics_models import (
    BaseDynamicsModel,
    DynamicsModelManager,
)  # TODO (yinda): resolve this hard-code
from simulator.trajectory.random_walk import random_walk
from simulator.trajectory.reference_line import ReferenceLineManager
from simulator.observation.observation_manager import ObservationManager
from drltt_proto.environment.trajectory_tracking_pb2 import TrajectoryTrackingEnvironment, TrajectoryTrackingHyperParameter


@ENVIRONMENTS.register
class TrajectoryTrackingEnv(gym.Env):
    # dynamics_model: BaseDynamicsModel
    state_space: Space = None
    init_state_space: Space = None
    action_space: Space = None  # required by learning algorithm
    observation_space: Space = None  # required by learning algorithm
    env_info: TrajectoryTrackingEnvironment

    def __init__(
        self,
        dynamics_model_configs: List[Dict[str, Any]],
        **kwargs,
    ):
        """
        Args:
            step_interval: step interval by which each step moves forward temporally
            dynamics_model_configs: dynamics model's configs (to be sampled during training time)
            init_state_lb: lower bound of state space
            init_state_ub: upper bound of state space
            n_observation_steps: number of the steps within the observation
            reward_configs: config of all rewards
        """
        # parse hyper-parameters
        self.env_info = TrajectoryTrackingEnvironment()
        self.parse_hyper_parameter(self.env_info.hyper_parameter, **kwargs)

        # build manager classes
        self.reference_line_manager = ReferenceLineManager(
            n_observation_steps=self.env_info.hyper_parameter.n_observation_steps,
        )
        self.dynamics_model_manager = DynamicsModelManager(
            dynamics_model_configs=dynamics_model_configs,
        )
        self.observation_manager = ObservationManager(
            self.reference_line_manager,
            self.dynamics_model_manager,
        )

        # build spaces
        self._build_spaces()

    @classmethod
    def parse_hyper_parameter(
        cls,
        hyper_parameter: TrajectoryTrackingHyperParameter,
        step_interval: float,
        tracking_length_lb: int,
        tracking_length_ub: int,
        init_state_lb: List[Union[float, None]],
        init_state_ub: List[Union[float, None]],
        n_observation_steps: int,
    ):
        hyper_parameter.step_interval = step_interval
        hyper_parameter.tracking_length_lb = tracking_length_lb
        hyper_parameter.tracking_length_ub = tracking_length_ub
        hyper_parameter.init_state_lb.extend(init_state_lb)
        hyper_parameter.init_state_ub.extend(init_state_ub)
        hyper_parameter.n_observation_steps = n_observation_steps

    @override
    def reset(
        self,
        seed: int = None,
        init_state: np.ndarray = None,
    ):
        extra_info = dict()

        self.env_info.runtime_data.step_index = 0

        # TODO: decide whether keep a handler to the sampled dynamics model in env object
        sampled_dynamics_model: BaseDynamicsModel = self.dynamics_model_manager.sample_dynamics_model()

        tracking_length = random.randint(
            self.env_info.hyper_parameter.tracking_length_lb,
            self.env_info.hyper_parameter.tracking_length_ub,
        )
        self.env_info.runtime_data.tracking_length = tracking_length

        init_state = self.init_state_space.sample()
        sampled_dynamics_model.set_state(init_state)
        reference_dynamics_model = deepcopy(sampled_dynamics_model)
        reference_line, trajectory = random_walk(
            dynamics_model=reference_dynamics_model,
            step_interval=self.env_info.hyper_parameter.step_interval,
            walk_length=tracking_length + self.env_info.hyper_parameter.n_observation_steps,  # TODO: verify the number
        )
        self.reference_line_manager.set_reference_line(reference_line)

        # TODO: use closest waypoint assignment

        observation = self.observation_manager.get_observation(
            index=self.env_info.runtime_data.step_index,
            body_state=sampled_dynamics_model.get_body_state_proto(),
        )
        # TODO: verify interface: gym==0.21 or gym==0.26
        # reference: https://gymnasium.farama.org/content/migration-guide/

        # return observation, extra_info
        return observation

    def _build_spaces(
        self,
    ):
        """
        Build spaces (observation / action / state / init_state / etc.)

        Dependency (class attributes needed to be set before):
        - self.env_info
        - self.dynamics_model_manager
        - self.observation_manager
        """
        if self.observation_space is None:
            self.observation_space = self.observation_manager.get_observation_space()
        if self.action_space is None:
            self.action_space = self.dynamics_model_manager.get_sampled_dynamics_model().get_action_space()
        if self.state_space is None:
            self.state_space = self.dynamics_model_manager.get_sampled_dynamics_model().get_state_space()
        if self.init_state_space is None:
            self.init_state_space = gym.spaces.Box(
                low=np.array((self.env_info.hyper_parameter.init_state_lb), dtype=DTYPE),
                high=np.array((self.env_info.hyper_parameter.init_state_ub), dtype=DTYPE),
                dtype=DTYPE,
            )

    def get_current_dynamics_model(self) -> BaseDynamicsModel:
        return self.dynamics_model_manager.get_sampled_dynamics_model()

    @override
    def step(self, action: np.ndarray):
        """
        TODO: verify this function
        """
        extra_info = dict()

        current_dynamics_model = self.get_current_dynamics_model()

        # TODO configurable reward weighting
        all_rewards = dict()
        # tracking
        state_vec: np.ndarray = current_dynamics_model.get_state()
        waypoint_vec = self.reference_line_manager.get_reference_line_waypoint(self.env_info.runtime_data.step_index)
        dist = np.linalg.norm(state_vec[:2] - waypoint_vec)
        all_rewards['tracking'] = -dist
        # TODO: add heading error
        # action
        action_space = current_dynamics_model.get_action_space()
        normalized_action = (action - action_space.low) / (action_space.high - action_space.low)
        all_rewards['action'] = -(normalized_action**2).sum()
        # sum up
        scalar_reward = sum(all_rewards.values())
        extra_info['all_rewards'] = all_rewards

        # update state
        current_dynamics_model.step(action, delta_t=self.env_info.hyper_parameter.step_interval)
        self.env_info.runtime_data.step_index += 1
        observation = self.observation_manager.get_observation(
            index=self.env_info.runtime_data.step_index,
            body_state=current_dynamics_model.get_body_state_proto(),
        )

        terminated: bool = self.env_info.runtime_data.step_index >= self.env_info.runtime_data.tracking_length
        truncated: bool = False

        # TODO: verify interface: gym==0.21 or gym==0.26
        # reference: https://gymnasium.farama.org/content/migration-guide/

        # return observation, scalar_reward, terminated, truncated, extra_info
        return observation, scalar_reward, terminated, extra_info

    # TODO: rendering
