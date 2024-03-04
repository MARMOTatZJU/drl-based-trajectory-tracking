import os
import shutil

from gym import Env

from common import build_object_within_registry_from_config
from common.io import load_and_override_configs, generate_random_string

from simulator import TEST_CONFIG_PATHS
from simulator.environments import ENVIRONMENTS
from simulator.rl_learning.sb3_learner import build_sb3_algorithm_from_config, train_with_sb3, eval_with_sb3


# TODO: use pytest fixture/setup to refactor tests within file, to avoid copy-paste of test codes
# TODO: use unit-test config to override sample config.


def test_train_with_sb3():
    config = load_and_override_configs(TEST_CONFIG_PATHS)

    env_config = config['environment']
    environment: Env = build_object_within_registry_from_config(ENVIRONMENTS, env_config)
    config['learning']['total_timesteps'] = 64
    config['algorithm']['learning_starts'] = 16
    config['algorithm']['batch_size'] = 16
    test_checkpoint_dir = f'/tmp/drltt-pytest-{generate_random_string(6)}'
    test_checkpoint_file_prefix = f'{test_checkpoint_dir}/checkpoint'
    algorithm = train_with_sb3(
        environment=environment,
        algorithm_config=config['algorithm'],
        learning_config=config['learning'],
        checkpoint_file_prefix=test_checkpoint_file_prefix,
    )
    shutil.rmtree(test_checkpoint_dir)


def test_eval_with_sb3():
    config = load_and_override_configs(TEST_CONFIG_PATHS)

    env_config = config['environment']
    environment: Env = build_object_within_registry_from_config(ENVIRONMENTS, env_config)
    algorithm_config = config['algorithm']
    algorithm = build_sb3_algorithm_from_config(environment, algorithm_config)

    eval_config = config['evaluation']['eval_config']
    eval_config['n_episodes'] = 10
    report_dir = f'/tmp/drltt-pytest-{generate_random_string(6)}'
    eval_with_sb3(environment, algorithm, report_dir, **eval_config)
    if os.path.exists(report_dir):
        shutil.rmtree(report_dir, ignore_errors=True)


if __name__ == '__main__':
    test_train_with_sb3()
    test_eval_with_sb3()
