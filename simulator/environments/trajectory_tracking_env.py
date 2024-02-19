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
from simulator import DTYPE
from simulator.dynamics_models import (
    BaseDynamicsModel,
    DynamicsModelManager,
)  # TODO (yinda): resolve this hard-code
from simulator.trajectory.random_walk import random_walk
from simulator.trajectory.reference_line import ReferenceLineManager
from simulator.observation.observation_manager import ObservationManager
from drltt_proto.environment.trajectory_tracking_pb2 import (
    TrajectoryTrackingEnvironment,
    TrajectoryTrackingHyperParameter,
    TrajectoryTrackingEpisode,
)


@ENVIRONMENTS.register
class TrajectoryTrackingEnv(gym.Env):
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
    env_info: TrajectoryTrackingEnvironment

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
        """Parse hyper-parameter.

        Args:
            hyper_parameter: Destination of the parsed hyper-parameters.
            step_interval: Step interval by which each step moves forward temporally.
            tracking_length_lb: Lower bound of tracking length.
            tracking_length_ub: Upper bound of tracking length.
            init_state_lb: lower Bound of state space.
            init_state_ub: upper Bound of state space.
            n_observation_steps: Number of the steps within the observation.
        """
        hyper_parameter.step_interval = step_interval
        hyper_parameter.tracking_length_lb = tracking_length_lb
        hyper_parameter.tracking_length_ub = tracking_length_ub
        hyper_parameter.init_state_lb.extend(init_state_lb)
        hyper_parameter.init_state_ub.extend(init_state_ub)
        hyper_parameter.n_observation_steps = n_observation_steps

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

        # clearn data in old episode
        self.env_info.episode.Clear()
        # reset data in old episode
        self.env_info.episode.step_index = 0
        self.env_info.episode.hyper_parameter.CopyFrom(self.env_info.hyper_parameter)

        # TODO: decide whether keep a handler to the sampled dynamics model in env object
        sampled_dynamics_model: BaseDynamicsModel = self.dynamics_model_manager.sample_dynamics_model()
        self.env_info.episode.dynamics_model.type = type(sampled_dynamics_model).__name__

        tracking_length = random.randint(
            self.env_info.hyper_parameter.tracking_length_lb,
            self.env_info.hyper_parameter.tracking_length_ub,
        )
        self.env_info.episode.tracking_length = tracking_length

        if init_state is None:
            init_state = self.init_state_space.sample()
        sampled_dynamics_model.set_state(init_state)
        reference_dynamics_model = deepcopy(sampled_dynamics_model)
        reference_line, trajectory = random_walk(
            dynamics_model=reference_dynamics_model,
            step_interval=self.env_info.hyper_parameter.step_interval,
            walk_length=tracking_length + self.env_info.hyper_parameter.n_observation_steps,  # TODO: verify the number
        )
        self.reference_line_manager.set_reference_line(reference_line)
        self.env_info.episode.reference_line.CopyFrom(reference_line)

        # TODO: use closest waypoint assignment

        observation = self.observation_manager.get_observation(
            index=self.env_info.episode.step_index,
            body_state=sampled_dynamics_model.get_body_state_proto(),
        )
        # TODO: verify interface: gym==0.21 or gym==0.26
        # reference: https://gymnasium.farama.org/content/migration-guide/

        # return observation, extra_info
        return observation

    def _build_spaces(self):
        """
        Build spaces (observation/action/state/init_state / etc.).

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
        Args:
            action: Action given to the environment for stepping the state.
        """
        extra_info = dict()  # WARNING: `extra_info` can not store large object

        current_dynamics_model = self.get_current_dynamics_model()

        # TODO configurable reward weighting
        all_rewards = dict()
        # tracking
        state_vec: np.ndarray = current_dynamics_model.get_state()
        waypoint_vec = self.reference_line_manager.get_reference_line_waypoint(self.env_info.episode.step_index)
        dist = np.linalg.norm(state_vec[:2] - waypoint_vec)
        all_rewards['tracking'] = -dist
        # TODO: add heading error
        # action
        scaled_action = scale_action(action, current_dynamics_model.get_action_space())

        all_rewards['action'] = -(scaled_action**2).sum()
        # sum up
        scalar_reward = sum(all_rewards.values())
        extra_info['all_rewards'] = all_rewards

        self.env_info.episode.dynamics_model.states.append(deepcopy(current_dynamics_model.get_state_proto()))
        self.env_info.episode.dynamics_model.actions.append(deepcopy(current_dynamics_model.serialize_action(action)))
        self.env_info.episode.rewards.append(deepcopy(scalar_reward))

        # ABOVE: step t
        # BELLOW: step t+1

        # update state
        current_dynamics_model.step(action, delta_t=self.env_info.hyper_parameter.step_interval)
        self.env_info.episode.step_index += 1
        observation = self.observation_manager.get_observation(
            index=self.env_info.episode.step_index,
            body_state=current_dynamics_model.get_body_state_proto(),
        )

        terminated: bool = self.env_info.episode.step_index >= self.env_info.episode.tracking_length
        truncated: bool = False

        # TODO: verify interface: gym==0.21 or gym==0.26
        # reference: https://gymnasium.farama.org/content/migration-guide/

        # return observation, scalar_reward, terminated, truncated, extra_info
        return observation, scalar_reward, terminated, extra_info

    def export_episode_data(
        self,
    ) -> TrajectoryTrackingEpisode:
        """Export episode data.

        Return:
            TrajectoryTrackingEpisode: Episode data in proto structure.
        """
        episode_data = TrajectoryTrackingEpisode()
        episode_data.CopyFrom(self.env_info.episode)

        return episode_data

    # TODO: rendering
