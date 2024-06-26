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

from . import METRICS
from .sb3_utils import roll_out_one_episode

from drltt.common import Registry, build_object_within_registry_from_config
from drltt.common.gym_helper import scale_action
from drltt.simulator.environments import ExtendedGymEnv
from drltt.simulator.visualization import VISUALIZATION_FUNCTIONS

from drltt_proto.environment.environment_pb2 import Environment

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
        for _ in range(environment.env_info.trajectory_tracking.hyper_parameter.max_n_episodes + 1):
            roll_out_one_episode(environment, lambda obs: algorithm.predict(obs)[0])
        env_data = environment.export_environment_data()
        env_data_save_path = f'{checkpoint_dir}/env_data.bin'
        with open(env_data_save_path, 'wb') as f:
            f.write(env_data.SerializeToString())
        logging.info(f'Environment data saved to {env_data_save_path}')

    return algorithm


def eval_with_sb3(
    environment: gym.Env,
    algorithm: BaseAlgorithm,
    report_dir: str,
    n_episodes: int,
    compute_metrics_name: str,
    visualization_function_name: str,
    viz_interval: int = 10,
):
    """RL Evaluation with Stable Baselines3.

    Args:
        environment: Evaluation environment.
        algorithm: The algorithm with models to be evaluated.
        report_dir: Directory to export report JSON.
        n_episodes: Number of episodes.
        compute_metrics_name: Name of `compute_metrics`.
        visualization_function_name: Name of `visualization_function`.
        viz_interval: Interval of episodes that this function performs visualization.
            TODO: set it with argument passed through Shell script.
    """
    algorithm.set_logger(configure(f'{report_dir}/sb3-eval', format_strings=SB3_LOGGING_FORMAT_STRINGS))
    all_episodes_metrics = list()
    viz_dir = f"{report_dir}/visualization"
    os.makedirs(viz_dir, exist_ok=True)
    for scenario_idx in range(n_episodes):
        logging.info(f'scenario #{scenario_idx}')
        roll_out_one_episode(environment, lambda obs: algorithm.predict(obs)[0])

        compute_metrics = METRICS[compute_metrics_name]
        env_data: Environment = environment.export_environment_data()
        metrics = compute_metrics(env_data, environment)  # format: metric[metric_name][reduce_method]
        if scenario_idx % viz_interval == 0:
            # TODO: consider moving it to env.render()
            viz_prefix = f"{viz_dir}/{scenario_idx}"
            visualization_function = VISUALIZATION_FUNCTIONS[visualization_function_name]
            visualization_function(env_data, viz_prefix)
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
    env_data: Environment,
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
    assert isinstance(
        env_data, Environment
    ), f'`compute_bicycle_model_metrics` requires env_data to be in class `Environment`'
    episode = env_data.trajectory_tracking.episode

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
