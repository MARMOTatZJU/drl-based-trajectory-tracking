import argparse
import os
import sys
from copy import deepcopy
import logging
import shutil

import gym
from gym import Env
from stable_baselines3.common.base_class import BaseAlgorithm

from common import build_object_within_registry_from_config
from common.io import load_config_from_yaml, convert_list_to_tuple_within_dict, override_config
from simulator.rl_learning.sb3_learner import train_with_sb3, eval_with_sb3, build_sb3_algorithm_from_config
from simulator.environments import ENVIRONMENTS


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('--config-file', type=str)
    parser.add_argument('--checkpoint-dir', type=str)
    parser.add_argument('--train', action='store_true', default=False)
    parser.add_argument('--eval', action='store_true', default=False)

    args = parser.parse_args()

    return args


def configure_root_logger(log_dir: str):
    os.makedirs(log_dir, exist_ok=True)
    FORMAT = '%(asctime)s :: %(name)s :: %(levelname)-8s :: %(message)s'
    FORMATTER = logging.Formatter(fmt=FORMAT)

    logger = logging.root

    stream_handler = logging.StreamHandler(stream=sys.stdout)
    stream_handler.setFormatter(FORMATTER)
    stream_handler.setLevel(logging.INFO)
    logger.addHandler(stream_handler)

    file_handler = logging.FileHandler(filename=f'{log_dir}/log.txt')
    file_handler.setFormatter(FORMATTER)
    file_handler.setLevel(logging.INFO)
    logger.addHandler(file_handler)

    logging.info(f'Logging directory configured at: {log_dir}')


def main(args):
    configure_root_logger(args.checkpoint_dir)

    config = load_config_from_yaml(args.config_file)
    config = convert_list_to_tuple_within_dict(config)
    env_config = config['environment']

    # backup config
    os.makedirs(args.checkpoint_dir, exist_ok=True)
    shutil.copy(args.config_file, args.checkpoint_dir)

    checkpoint_file_prefix = f'{args.checkpoint_dir}/checkpoint'  # without extension

    if args.train:
        environment: Env = build_object_within_registry_from_config(ENVIRONMENTS, deepcopy(env_config))
        train_with_sb3(
            environment=environment,
            algorithm_config=deepcopy(config['algorithm']),
            learning_config=deepcopy(config['learning']),
            checkpoint_file_prefix=checkpoint_file_prefix,
        )

    if args.eval:
        eval_config = config['evaluation']
        eval_env_config = override_config(deepcopy(env_config), deepcopy(eval_config['overriden_environment']))
        eval_environment: Env = build_object_within_registry_from_config(ENVIRONMENTS, deepcopy(eval_env_config))

        eval_algorithm: BaseAlgorithm = build_sb3_algorithm_from_config(
            eval_environment,
            config['algorithm'],
        )
        eval_algorithm.load(checkpoint_file_prefix)

        eval_with_sb3(
            eval_environment,
            eval_algorithm,
            report_dir=args.checkpoint_dir,
            **eval_config['eval_config'],
        )


if __name__ == '__main__':
    args = parse_args()
    main(args)
