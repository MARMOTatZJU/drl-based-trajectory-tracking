from typing import List, Dict, Union, Any, Iterable
import os
import math
from copy import deepcopy
import random

import numpy as np
import gym
from gym.spaces import Space

from drltt.common.future import override
from drltt.common.gym_helper import scale_action
from drltt.common import GLOBAL_DEBUG_INFO
from . import ENVIRONMENTS
from drltt.simulator.environments.env_interface import CustomizedEnvInterface
from drltt.simulator import DTYPE
from drltt.simulator.dynamics_models import (
    BaseDynamicsModel,
    DynamicsModelManager,
)
from drltt.simulator.trajectory.random_walk import random_walk
from drltt.simulator.trajectory.reference_line import ReferenceLineManager
from drltt.simulator.observation.observation_manager import ObservationManager
from drltt_proto.environment.environment_pb2 import Environment
from drltt_proto.environment.trajectory_tracking_pb2 import (
    TrajectoryTrackingHyperParameter,
)
from drltt_proto.trajectory.trajectory_pb2 import ReferenceLine


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
        env_info: Union[Environment, None] = None,
        dynamics_model_configs: Union[Iterable[Dict[str, Any]], None] = None,
        **kwargs,
    ):
        """
        Args:
            dynamics_model_configs: Configurations of all dynamics models.
        """
        self.env_info = Environment()

        if env_info is not None:
            # TODO: add test for this branch
            self.env_info.CopyFrom(env_info)
        else:
            # parse hyper-parameters
            self.env_info = Environment()
            self.parse_hyper_parameter(self.env_info.trajectory_tracking.hyper_parameter, **kwargs)

        # build manager classes
        self.reference_line_manager = ReferenceLineManager(
            n_observation_steps=self.env_info.trajectory_tracking.hyper_parameter.n_observation_steps,
            pad_mode=self.env_info.trajectory_tracking.hyper_parameter.reference_line_pad_mode,
        )
        self.dynamics_model_manager = DynamicsModelManager(
            hyper_parameters=self.env_info.trajectory_tracking.hyper_parameter.dynamics_models_hyper_parameters,
            dynamics_model_configs=dynamics_model_configs,
        )
        # consider use `self.dynamics_model_manager` to parse
        self.parse_dynamics_model_hyper_parameter(
            self.env_info.trajectory_tracking.hyper_parameter, self.dynamics_model_manager
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
        """Parse the hyper-parameters of dynamics models from the manager.

        Args:
            hyper_parameter (TrajectoryTrackingHyperParameter): Hyper-parameter to store parsed info.
            dynamics_model_manager (DynamicsModelManager): Dynamics model manager.
        """
        del hyper_parameter.dynamics_models_hyper_parameters[:]
        for dynamics_model_hyper_parameger in dynamics_model_manager.get_all_hyper_parameters():
            dm_hparam = hyper_parameter.dynamics_models_hyper_parameters.add()
            dm_hparam.CopyFrom(dynamics_model_hyper_parameger)

    @override
    def reset(
        self,
        init_state: Union[np.ndarray, None] = None,
        dynamics_model_name: str = '',
        reference_line: Union[ReferenceLine, None] = None,
    ) -> np.ndarray:
        """Reset environment for Trajectory Tracking.

        - Clear and replace episode data.
        - Randomly sample a dynamics model.
        - Setup reference line and initial state.

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

        if len(dynamics_model_name) > 0:
            sampled_dynamics_model_index, sampled_dynamics_model = (
                self.dynamics_model_manager.select_dynamics_model_by_name(dynamics_model_name)
            )
        else:
            sampled_dynamics_model_index, sampled_dynamics_model = self.dynamics_model_manager.sample_dynamics_model()

        self.env_info.trajectory_tracking.episode.dynamics_model.type = type(sampled_dynamics_model).__name__
        self.env_info.trajectory_tracking.episode.dynamics_model.hyper_parameter.CopyFrom(
            sampled_dynamics_model.hyper_parameter
        )
        self.env_info.trajectory_tracking.episode.selected_dynamics_model_index = sampled_dynamics_model_index

        if reference_line is None:
            tracking_length = random.randint(
                self.env_info.trajectory_tracking.hyper_parameter.tracking_length_lb,
                self.env_info.trajectory_tracking.hyper_parameter.tracking_length_ub,
            )
            if init_state is None:
                init_state = self.init_state_space.sample()
            sampled_dynamics_model.set_state(init_state)
            reference_dynamics_model = deepcopy(sampled_dynamics_model)
            reference_line, trajectory = random_walk(
                dynamics_model=reference_dynamics_model,
                step_interval=self.env_info.trajectory_tracking.hyper_parameter.step_interval,
                walk_length=tracking_length,
            )
        else:
            tracking_length = len(reference_line.waypoints)
            if init_state is None:
                init_state = ReferenceLineManager.estimate_init_state_from_reference_line(
                    reference_line,
                    delta_t=self.env_info.trajectory_tracking.hyper_parameter.step_interval,
                )
            sampled_dynamics_model.set_state(init_state)
            # TODO: optional estimate from init state
        self.reference_line_manager.set_reference_line(reference_line, tracking_length=tracking_length)
        self.env_info.trajectory_tracking.episode.tracking_length = tracking_length
        self.env_info.trajectory_tracking.episode.reference_line.CopyFrom(
            self.reference_line_manager.raw_reference_line
        )

        # TODO: use closest waypoint assignment for observation
        observation = self.observation_manager.get_observation(
            episode_data=self.env_info.trajectory_tracking.episode,
            body_state=sampled_dynamics_model.get_body_state_proto(),
        )
        self.env_info.trajectory_tracking.episode.dynamics_model.observations.append(
            deepcopy(sampled_dynamics_model.serialize_observation(observation))
        )

        # TODO: verify interface: gym==0.21 or gym==0.26
        # reference: https://gymnasium.farama.org/content/migration-guide/

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
        self.env_info.trajectory_tracking.episode.dynamics_model.debug_infos.append(deepcopy(GLOBAL_DEBUG_INFO))
        GLOBAL_DEBUG_INFO.Clear()

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
    def get_state(self) -> np.ndarray:
        return self.dynamics_model_manager.get_sampled_dynamics_model().get_state()

    def get_dynamics_model_info(self) -> str:
        """Get the infromation about configuration of dynamics models.

        Returns:
            str: Pretty string of information for dynamics models.
        """
        return self.dynamics_model_manager.get_dynamics_model_info()

    def get_reference_line(self) -> ReferenceLine:
        """Get the current reference line.

        Returns:
            ReferenceLine: The current reference line.
        """
        reference_line = ReferenceLine()
        reference_line.CopyFrom(self.reference_line_manager.raw_reference_line)

        return reference_line

    # TODO: rendering
    # refernce: https://github.com/openai/gym/blob/dcd185843a62953e27c2d54dc8c2d647d604b635/gym/core.py#L153
