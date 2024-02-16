import argparse

import gym
from gym import Env

from common import build_object_within_registry_from_config
from common.io import load_config_from_yaml, convert_list_to_tuple_within_dict
from simulator.rl_learning.sb3_learner import train_with_sb3
from simulator.environments import ENVIRONMENTS


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('--config-file', type=str)
    parser.add_argument('--checkpoint-file', type=str)
    args = parser.parse_args()

    return args


def main(args):
    config = load_config_from_yaml(args.config_file)
    config = convert_list_to_tuple_within_dict(config)
    env_config = config['environment']
    environment: Env = build_object_within_registry_from_config(ENVIRONMENTS, env_config)

    model = train_with_sb3(
        environment=environment,
        model_config=config['model'],
        learning_config=config['learning'],
        checkpoint_file=args.checkpoint_file,
    )


if __name__ == '__main__':
    args = parse_args()
    main(args)
