from typing import List
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
from common.io import load_and_override_configs, override_config, save_config_to_yaml
from simulator.rl_learning.sb3_learner import train_with_sb3, eval_with_sb3, build_sb3_algorithm_from_config
from simulator.rl_learning.sb3_export import export_sb3_jit_module
from simulator.environments import ENVIRONMENTS, ExtendedGymEnv
from simulator.rl_learning.sb3_learner import SB3_MODULES


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '--config-files',
        metavar='N',
        type=str,
        nargs='+',
        help=(
            'Config file(s). If multiple paths provided, the first config is base and will overridden by the rest'
            ' respectively.'
        ),
    )
    parser.add_argument('--checkpoint-dir', type=str)
    parser.add_argument('--train', action='store_true', default=False)
    parser.add_argument('--eval', action='store_true', default=False)
    parser.add_argument('--trace', action='store_true', default=False)
    parser.add_argument('--test-case-save-format', type=str, default='protobuf')
    parser.add_argument('--num-test-cases', type=int, default=1)

    args = parser.parse_args()

    return args


def configure_root_logger(log_dir: str):
    """Configure root logger.

    Remove all default handlers and add customized handlers.

    Args:
        log_dir: Directory to dump log output.
    """
    os.makedirs(log_dir, exist_ok=True)
    FORMAT = '%(asctime)s :: %(name)s :: %(levelname)-8s :: %(message)s'
    FORMATTER = logging.Formatter(fmt=FORMAT)

    logger = logging.root
    logger.handlers.clear()

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

    config = load_and_override_configs(args.config_files)
    env_config = config['environment']

    # backup config
    os.makedirs(args.checkpoint_dir, exist_ok=True)
    save_config_to_yaml(config, f'{args.checkpoint_dir}/config.yaml')
    for i_config, config_p in enumerate(args.config_files):
        config_basename = os.path.basename(config_p)
        config_save_path = f'{i_config:02}-{config_basename}'
        shutil.copy(config_p, f'{args.checkpoint_dir}/{config_save_path}')
        logging.info(f'Config file backed up at: {config_save_path}')

    checkpoint_file_prefix = f'{args.checkpoint_dir}/checkpoint'  # without extension

    if args.train:
        environment: ExtendedGymEnv = build_object_within_registry_from_config(ENVIRONMENTS, deepcopy(env_config))
        train_with_sb3(
            environment=environment,
            algorithm_config=deepcopy(config['algorithm']),
            learning_config=deepcopy(config['learning']),
            checkpoint_file_prefix=checkpoint_file_prefix,
        )

    if args.eval:
        eval_config = config['evaluation']
        eval_env_config = override_config(deepcopy(env_config), deepcopy(eval_config['overriden_environment']))
        eval_environment: ExtendedGymEnv = build_object_within_registry_from_config(
            ENVIRONMENTS, deepcopy(eval_env_config)
        )

        eval_algorithm: BaseAlgorithm = SB3_MODULES[config['algorithm']['type']].load(checkpoint_file_prefix)

        eval_with_sb3(
            eval_environment,
            eval_algorithm,
            report_dir=args.checkpoint_dir,
            **eval_config['eval_config'],
        )

    if args.trace:
        trace_algorithm: BaseAlgorithm = SB3_MODULES[config['algorithm']['type']].load(checkpoint_file_prefix)
        trace_environment: ExtendedGymEnv = build_object_within_registry_from_config(ENVIRONMENTS, deepcopy(env_config))
        export_sb3_jit_module(
            trace_algorithm,
            trace_environment,
            device='cpu',
            export_dir=args.checkpoint_dir,
            n_test_cases=args.num_test_cases,
            test_case_save_format=args.test_case_save_format,
        )


if __name__ == '__main__':
    args = parse_args()
    main(args)
