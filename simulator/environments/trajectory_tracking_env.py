from typing import List, Tuple, Dict, Union, Any, Optional, Generator, override
import os
import math
from copy import deepcopy
import random

import numpy as np
import gym
from gym.spaces import Space

from common.gym_helper import scale_action
from . import ENVIRONMENTS
from simulator.environments.env_interface import CustomizedEnvInterface
from simulator import DTYPE
from simulator.dynamics_models import (
    BaseDynamicsModel,
    DynamicsModelManager,
)
from simulator.trajectory.random_walk import random_walk
from simulator.trajectory.reference_line import ReferenceLineManager
from simulator.observation.observation_manager import ObservationManager
from drltt_proto.environment.environment_pb2 import Environment
from drltt_proto.environment.trajectory_tracking_pb2 import (
    TrajectoryTrackingHyperParameter,
    TrajectoryTrackingEpisode,
)


@ENVIRONMENTS.register
class TrajectoryTrackingEnv(gym.Env, CustomizedEnvInterface):
    """Environment for Trajectory Tracking.

    Attributes:
        observation_space: State space, utilized by RL framework such as Stable Baselines3.
        action_space: State space, utilized by RL framework such as Stable Baselines3.
        state_space: State space.
        init_state_space: Initial state space.
        env_info: Serialized data structure that contains hyper-parameter and episode data.
    """

    state_space: Space = None
    init_state_space: Space = None
    action_space: Space = None
    observation_space: Space = None

    def __init__(
        self,
        dynamics_model_configs: List[Dict[str, Any]],
        **kwargs,
    ):
        """
        Args:
            dynamics_model_configs: Configurations of all dynamics models.
        """
        # parse hyper-parameters
        self.env_info = Environment()
        self.parse_hyper_parameter(self.env_info.trajectory_tracking.hyper_parameter, **kwargs)

        # build manager classes
        self.reference_line_manager = ReferenceLineManager(
            n_observation_steps=self.env_info.trajectory_tracking.hyper_parameter.n_observation_steps,
            pad_mode=self.env_info.trajectory_tracking.hyper_parameter.reference_line_pad_mode,
        )
        self.dynamics_model_manager = DynamicsModelManager(
            dynamics_model_configs=dynamics_model_configs,
        )
        self.observation_manager = ObservationManager(
            self.reference_line_manager,
            self.dynamics_model_manager,
        )

        self.parse_dynamics_model_hyper_parameter(
            self.env_info.trajectory_tracking.hyper_parameter, self.dynamics_model_manager
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
        reference_line_pad_mode: str,
        init_state_lb: List[Union[float, None]],
        init_state_ub: List[Union[float, None]],
        n_observation_steps: int,
        max_n_episodes: int = 1000,
    ):
        """Parse hyper-parameter.

        Args:
            hyper_parameter: Destination of the parsed hyper-parameters.
            step_interval: Step interval by which each step moves forward temporally.
            tracking_length_lb: Lower bound of tracking length.
            tracking_length_ub: Upper bound of tracking length.
            reference_line_pad_mode: Mode for padding reference line.
            init_state_lb: lower Bound of state space.
            init_state_ub: upper Bound of state space.
            n_observation_steps: Number of the steps within the observation.
        """
        hyper_parameter.step_interval = step_interval
        hyper_parameter.tracking_length_lb = tracking_length_lb
        hyper_parameter.tracking_length_ub = tracking_length_ub
        hyper_parameter.reference_line_pad_mode = reference_line_pad_mode
        hyper_parameter.init_state_lb.extend(init_state_lb)
        hyper_parameter.init_state_ub.extend(init_state_ub)
        hyper_parameter.n_observation_steps = n_observation_steps
        hyper_parameter.max_n_episodes = max_n_episodes

    @classmethod
    def parse_dynamics_model_hyper_parameter(
        cls,
        hyper_parameter: TrajectoryTrackingHyperParameter,
        dynamics_model_manager: DynamicsModelManager,
    ):
        """TODO: docstring"""
        for dynamics_model_hyper_parameger in dynamics_model_manager.get_all_hyper_parameters():
            dm_hparam = hyper_parameter.dynamics_models_hyper_parameters.add()
            dm_hparam.CopyFrom(dynamics_model_hyper_parameger)

    @override
    def reset(
        self,
        init_state: Union[np.ndarray, None] = None,
    ) -> np.ndarray:
        """Reset environment for Trajectory Tracking.

        - Setup reference line
        - Clear and replace self episode
        - Randomly sample a dynamics model

        Args:
            init_state: Specified initial state of dynamics model. Default to `None` which denotes random sampling from pre-defined initial state space.

        Returns:
            np.ndarray: First observation from the environment.
        """
        extra_info = dict()

        # store previous episode
        if self.env_info.trajectory_tracking.episode.step_index > 0:
            self.env_info.trajectory_tracking.episodes.append(self.env_info.trajectory_tracking.episode)
        while (
            len(self.env_info.trajectory_tracking.episodes)
            > self.env_info.trajectory_tracking.hyper_parameter.max_n_episodes
        ):
            self.env_info.trajectory_tracking.episodes.pop(0)

        # clear data
        self.env_info.trajectory_tracking.episode.Clear()
        # reset data
        self.env_info.trajectory_tracking.episode.step_index = 0
        self.env_info.trajectory_tracking.episode.hyper_parameter.CopyFrom(
            self.env_info.trajectory_tracking.hyper_parameter
        )

        sampled_dynamics_model_index, sampled_dynamics_model = self.dynamics_model_manager.sample_dynamics_model()
        self.env_info.trajectory_tracking.episode.dynamics_model.type = type(sampled_dynamics_model).__name__
        self.env_info.trajectory_tracking.episode.dynamics_model.hyper_parameter.CopyFrom(
            sampled_dynamics_model.hyper_parameter
        )
        self.env_info.trajectory_tracking.episode.selected_dynamics_model_index = sampled_dynamics_model_index

        tracking_length = random.randint(
            self.env_info.trajectory_tracking.hyper_parameter.tracking_length_lb,
            self.env_info.trajectory_tracking.hyper_parameter.tracking_length_ub,
        )
        self.env_info.trajectory_tracking.episode.tracking_length = tracking_length

        if init_state is None:
            init_state = self.init_state_space.sample()
        sampled_dynamics_model.set_state(init_state)
        reference_dynamics_model = deepcopy(sampled_dynamics_model)
        reference_line, trajectory = random_walk(
            dynamics_model=reference_dynamics_model,
            step_interval=self.env_info.trajectory_tracking.hyper_parameter.step_interval,
            walk_length=tracking_length,
        )
        self.reference_line_manager.set_reference_line(reference_line, tracking_length=tracking_length)
        self.env_info.trajectory_tracking.episode.reference_line.CopyFrom(
            self.reference_line_manager.raw_reference_line
        )

        # TODO: use closest waypoint assignment

        observation = self.observation_manager.get_observation(
            episode_data=self.env_info.trajectory_tracking.episode,
            body_state=sampled_dynamics_model.get_body_state_proto(),
        )
        # TODO: verify interface: gym==0.21 or gym==0.26
        # reference: https://gymnasium.farama.org/content/migration-guide/

        self.env_info.trajectory_tracking.episode.dynamics_model.observations.append(
            deepcopy(sampled_dynamics_model.serialize_observation(observation))
        )

        # return observation, extra_info
        return observation

    def _build_spaces(self):
        """
        Build spaces (observation/action/state/init_state/etc.).

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
                low=np.array((self.env_info.trajectory_tracking.hyper_parameter.init_state_lb), dtype=DTYPE),
                high=np.array((self.env_info.trajectory_tracking.hyper_parameter.init_state_ub), dtype=DTYPE),
                dtype=DTYPE,
            )

    def get_current_dynamics_model(self) -> BaseDynamicsModel:
        return self.dynamics_model_manager.get_sampled_dynamics_model()

    @override
    def step(self, action: np.ndarray):
        """
        Args:
            action: Action given to the environment for stepping the state.
        """
        extra_info = dict()  # WARNING: `extra_info` can not store large object

        current_dynamics_model = self.get_current_dynamics_model()

        # TODO configurable reward weighting
        all_rewards = dict()
        # tracking
        state_vec: np.ndarray = current_dynamics_model.get_state()
        waypoint_vec = self.reference_line_manager.get_reference_line_waypoint(
            self.env_info.trajectory_tracking.episode.step_index
        )
        dist = np.linalg.norm(state_vec[:2] - waypoint_vec)
        all_rewards['tracking'] = -dist
        # TODO: add heading error
        # action
        scaled_action = scale_action(action, current_dynamics_model.get_action_space())

        all_rewards['action'] = -(scaled_action**2).sum()
        # sum up
        scalar_reward = sum(all_rewards.values())
        extra_info['all_rewards'] = all_rewards

        self.env_info.trajectory_tracking.episode.dynamics_model.states.append(
            deepcopy(current_dynamics_model.get_state_proto())
        )
        self.env_info.trajectory_tracking.episode.dynamics_model.actions.append(
            deepcopy(current_dynamics_model.serialize_action(action))
        )
        self.env_info.trajectory_tracking.episode.rewards.append(deepcopy(scalar_reward))
        self.env_info.trajectory_tracking.episode.dynamics_model.debug_infos.append(
            deepcopy(current_dynamics_model.get_debug_info())
        )

        # ABOVE: step t
        # BELLOW: step t+1

        # update state
        current_dynamics_model.step(action, delta_t=self.env_info.trajectory_tracking.hyper_parameter.step_interval)
        self.env_info.trajectory_tracking.episode.step_index += 1
        observation = self.observation_manager.get_observation(
            episode_data=self.env_info.trajectory_tracking.episode,
            body_state=current_dynamics_model.get_body_state_proto(),
        )

        terminated: bool = (
            self.env_info.trajectory_tracking.episode.step_index
            >= self.env_info.trajectory_tracking.episode.tracking_length
        )
        truncated: bool = False

        if not terminated:
            self.env_info.trajectory_tracking.episode.dynamics_model.observations.append(
                deepcopy(current_dynamics_model.serialize_observation(observation))
            )
        # TODO: verify interface: gym==0.21 or gym==0.26
        # reference: https://gymnasium.farama.org/content/migration-guide/

        # return observation, scalar_reward, terminated, truncated, extra_info
        return observation, scalar_reward, terminated, extra_info

    @override
    def export_environment_data(
        self,
    ) -> Environment:
        """Export environment data.

        Return:
            Environment: Environment data in proto structure.
        """
        env_data = Environment()
        env_data.CopyFrom(self.env_info)

        return env_data

    # TODO: rendering
