import os
import shutil

from gym import Env

from common import build_object_within_registry_from_config
from common.io import load_config_from_yaml, convert_list_to_tuple_within_dict, generate_random_string
from simulator import SAMPLE_CONFIG_PATH
from simulator.environments import ENVIRONMENTS
from simulator.rl_learning.sb3_learner import build_sb3_algorithm_from_config, train_with_sb3, eval_with_sb3


# TODO: use pytest fixture/steup to refactor tests within file, to avoid copy-paste of test codes


def test_train_with_sb3():
    config_file = SAMPLE_CONFIG_PATH
    config = load_config_from_yaml(config_file)
    config = convert_list_to_tuple_within_dict(config)
    env_config = config['environment']
    environment: Env = build_object_within_registry_from_config(ENVIRONMENTS, env_config)
    config['learning']['total_timesteps'] = 64
    config['algorithm']['learning_starts'] = 16
    config['algorithm']['batch_size'] = 16
    test_checkpoint_dir = f'/tmp/drltt-pytest-{generate_random_string(6)}'
    test_checkpoint_file = f'{test_checkpoint_dir}/checkpoint.pkl'
    algorithm = train_with_sb3(
        environment=environment,
        algorithm_config=config['algorithm'],
        learning_config=config['learning'],
        checkpoint_file=test_checkpoint_file,
    )
    shutil.rmtree(test_checkpoint_dir)


def test_eval_with_sb3():
    config_file = SAMPLE_CONFIG_PATH
    config = load_config_from_yaml(config_file)
    config = convert_list_to_tuple_within_dict(config)
    env_config = config['environment']
    environment: Env = build_object_within_registry_from_config(ENVIRONMENTS, env_config)
    algorithm_config = config['algorithm']
    algorithm = build_sb3_algorithm_from_config(environment, algorithm_config)

    eval_config = config['evaluation']
    eval_config['n_episodes'] = 10
    report_dir = f'/tmp/drltt-pytest-{generate_random_string(6)}'
    eval_with_sb3(environment, algorithm, report_dir, **eval_config)
    if os.path.exists(report_dir):
        shutil.rmtree(report_dir, ignore_errors=True)


if __name__ == '__main__':
    test_train_with_sb3()
    test_eval_with_sb3()
