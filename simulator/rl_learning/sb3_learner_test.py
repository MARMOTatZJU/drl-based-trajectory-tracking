from gym import Env

from common import build_object_within_registry_from_config
from common.io import load_config_from_yaml, convert_list_to_tuple_within_dict
from simulator.rl_learning.sb3_learner import train_with_sb3

from simulator import SAMPLE_CONFIG_PATH
from simulator.environments import ENVIRONMENTS


def test_train_with_sb3():
    config_file = SAMPLE_CONFIG_PATH
    config = load_config_from_yaml(config_file)
    config = convert_list_to_tuple_within_dict(config)
    env_config = config['environment']

    environment: Env = build_object_within_registry_from_config(ENVIRONMENTS, env_config)
    config['learning']['total_timesteps'] = 5000
    model = train_with_sb3(
        environment=environment,
        model_config=config['model'],
        learning_config=config['learning'],
        checkpoint_file='',
    )

if __name__ == '__main__':
    test_train_with_sb3()
