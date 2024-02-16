from typing import Dict, Union
import os
import logging

import numpy as np

from common import Registry, build_object_within_registry_from_config
import gym
import stable_baselines3
from stable_baselines3.common.base_class import BaseAlgorithm
from stable_baselines3.common.noise import NormalActionNoise

SB3_MODULES = Registry().register_from_python_module(stable_baselines3)


def train_with_sb3(
    environment: gym.Env,
    model_config: Dict,
    learning_config: Dict,
    checkpoint_file: str = '',
) -> Union[BaseAlgorithm, None]:
    if os.path.exists(checkpoint_file):
        logging.warn(f'Training aborted as checkpoint exists: {checkpoint_file}')
        return None

    # add action noise object
    action_noise_config = model_config.pop('scaled_action_noise')
    model_config['action_noise'] = NormalActionNoise(
        mean=np.array(action_noise_config['mean']),
        sigma=np.array(action_noise_config['sigma']),
    )
    # add environment object
    model_config['env'] = environment

    # build model object
    model: BaseAlgorithm = build_object_within_registry_from_config(SB3_MODULES, model_config)

    logging.info(f'model.policy: {model.policy}')
    model.learn(**learning_config)

    if checkpoint_file != '':
        checkpoint_dir = os.path.dirname(checkpoint_file)
        os.makedirs(checkpoint_dir, exist_ok=True)
        model.save(checkpoint_file)
        logging.info(f'SB3 Model/Policy saved at: {checkpoint_file}')

    return model
