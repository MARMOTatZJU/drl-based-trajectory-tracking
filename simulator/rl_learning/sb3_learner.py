from typing import List, Tuple, Dict, Union, Any
import os
import logging
from copy import deepcopy
import json

import numpy as np
import pandas as pd
import gym
import stable_baselines3
from stable_baselines3.common.utils import configure
from stable_baselines3.common.base_class import BaseAlgorithm
from stable_baselines3.common.noise import NormalActionNoise

from common import Registry, build_object_within_registry_from_config
from common.gym_helper import scale_action
from simulator.environments import ExtendedGymEnv
from . import METRICS

from drltt_proto.environment.trajectory_tracking_pb2 import TrajectoryTrackingEpisode

SB3_MODULES = Registry().register_from_python_module(stable_baselines3)
SB3_LOGGING_FORMAT_STRINGS = ['stdout', 'log', 'csv']


def build_sb3_algorithm_from_config(
    environment: gym.Env,
    algorithm_config: Dict,
) -> BaseAlgorithm:
    """Build an algorithm from Stable Baselines 3.

    Args:
        environment: The associated environment.
        algorithm_config: The algorihm config.

    Returns:
        BaseAlgorithm: Built algorithm.
    """
    # add action noise object
    # TODO: check existence of `scaled_action_noise`
    action_noise_config = algorithm_config.pop('scaled_action_noise')
    algorithm_config['action_noise'] = NormalActionNoise(
        mean=np.array(action_noise_config['mean']),
        sigma=np.array(action_noise_config['sigma']),
    )
    # add environment object
    algorithm_config['env'] = environment

    # build algorithm object
    algorithm: BaseAlgorithm = build_object_within_registry_from_config(SB3_MODULES, algorithm_config)
    logging.info(f'Built algorithm.policy: {algorithm.policy}')

    return algorithm


def roll_out_one_episode(
    environment: gym.Env,
    algorithm: BaseAlgorithm,
) -> Tuple[List[np.ndarray], List[np.ndarray]]:
    """Roll out one episode and return a trajectory.

    Args:
        environment: The associated environment.
        algorithm_config: The algorihm config.
    Returns:
        List[np.ndarray]: Observations.
        List[np.ndarray]: Actions.
    """
    observations = list()
    actions = list()

    obs = environment.reset()
    observations.append(deepcopy(obs))
    done = False
    while not done:
        action, _states = algorithm.predict(obs)
        actions.append(deepcopy(action))
        obs, reward, done, info = environment.step(action)
        observations.append(deepcopy(obs))

    return observations, actions


def train_with_sb3(
    environment: ExtendedGymEnv,
    algorithm_config: Dict,
    learning_config: Dict,
    checkpoint_file_prefix: str = '',
) -> Union[BaseAlgorithm, None]:
    """RL Training with Stable Baselines3.

    Args:
        environment: Training environment.
        algorithm_config: Configuration of the algorithm.
        learning_config: Configuration of the learning.
        checkpoint_file_prefix: File prefix (i.e. path without extension) to save checkpoint file.

    Returns:
        Union[BaseAlgorithm, None]: The algorithm object with trained models.
    """
    checkpoint_file = f'{checkpoint_file_prefix}.zip'
    checkpoint_dir = os.path.dirname(checkpoint_file)
    if os.path.exists(checkpoint_file):
        logging.warn(f'Training aborted as checkpoint exists: {checkpoint_file}')
        return None

    algorithm = build_sb3_algorithm_from_config(environment, algorithm_config)
    algorithm.set_logger(configure(f'{checkpoint_dir}/sb3-train', format_strings=SB3_LOGGING_FORMAT_STRINGS))
    algorithm.learn(**learning_config)

    if checkpoint_file_prefix != '':
        # save model
        os.makedirs(checkpoint_dir, exist_ok=True)
        algorithm.save(checkpoint_file_prefix)
        logging.info(f'SB3 Algorithm Policy saved at: {checkpoint_file}')

        # save environment data
        roll_out_one_episode(environment, algorithm)
        env_data = environment.export_environment_data()
        env_data_save_path = f'{checkpoint_dir}/env_data.bin'
        with open(env_data_save_path, 'wb') as f:
            f.write(env_data.SerializeToString())
        logging.info('Environment data saved toL {}')

    return algorithm


def eval_with_sb3(
    environment: gym.Env,
    algorithm: BaseAlgorithm,
    report_dir: str,
    n_episodes: int,
    compute_metrics_name: str,
):
    """RL Evaluation with Stable Baselines3.

    Args:
        environment: Evaluation environment.
        algorithm: The algorithm with models to be evaluated.
        report_dir: Directory to export report JSON.
        n_episodes: Number of episodes.
        compute_metrics_name: Name of `compute_metrics`.
    """
    algorithm.set_logger(configure(f'{report_dir}/sb3-eval', format_strings=SB3_LOGGING_FORMAT_STRINGS))
    all_episodes_metrics = list()
    for scenario_idx in range(n_episodes):
        logging.info(f'scenario #{scenario_idx}')
        roll_out_one_episode(environment, algorithm)

        compute_metrics = METRICS[compute_metrics_name]
        episode: TrajectoryTrackingEpisode = environment.export_environment_data().episode
        metrics = compute_metrics(episode, environment)  # metric[metric_name][reduce_method]
        all_episodes_metrics.append(metrics)

    df = pd.DataFrame.from_records(all_episodes_metrics)
    json_str = df.median().to_json()

    os.makedirs(report_dir, exist_ok=True)
    report_file = f'{report_dir}/metrics.json'
    with open(report_file, 'w') as f:
        json.dump(json.loads(json_str), f, sort_keys=True, indent=2, separators=(',', ': '))

    logging.info(f'Report file dumped at: {report_file}')
    logging.info(json_str)


@METRICS.register
def compute_bicycle_model_metrics(
    episode: TrajectoryTrackingEpisode,
    environment: ExtendedGymEnv,
) -> Dict[str, Any]:
    """Compute metrics for the bicycle model for an episode.

    Args:
        episode: Data of the episode.
        environment: Associated environment.

    Returns:
        Dict[str, Any]: Computed metrics.

        - l2_distance_median: median L2 distance
        - scaled_action_norm_median
        - reward_median

    """
    dists = list()
    scaled_action_norms = list()
    rewards = list()
    for i_step in range(episode.tracking_length):
        reference_waypoint = episode.reference_line.waypoints[i_step]
        state = episode.dynamics_model.states[i_step]
        action = episode.dynamics_model.actions[i_step]
        reward = episode.rewards[i_step]
        tracked_position = np.array(
            (
                state.bicycle_model.body_state.x,
                state.bicycle_model.body_state.y,
            )
        )
        reference_position = np.array(
            (
                reference_waypoint.x,
                reference_waypoint.y,
            )
        )
        dist = np.linalg.norm(tracked_position - reference_position)

        action_vec = np.array((action.bicycle_model.a, action.bicycle_model.s))
        scaled_action = scale_action(action_vec, environment.action_space)
        scaled_action_norm = np.linalg.norm(scaled_action)

        dists.append(dist)
        scaled_action_norms.append(scaled_action_norm)
        rewards.append(reward)

    metrics = dict(
        l2_distance_median=np.median(dists),
        scaled_action_norm_median=np.median(scaled_action_norms),
        reward_median=np.median(rewards),
    )

    return metrics
