
from gym import Env

from common import build_object_within_registry_from_config
from common.io import load_and_override_configs, generate_random_string
from simulator import TEST_CONFIG_PATHS
from simulator.environments import ENVIRONMENTS
from simulator.rl_learning.sb3_learner import build_sb3_algorithm_from_config
from simulator.rl_learning.sb3_utils import roll_out_one_episode
from simulator.visualization.visualize_trajectory_tracking_episode import visualize_trajectory_tracking_episode
from drltt_proto.environment.environment_pb2 import Environment


def test_visualize_trajectory_tracking_episode():
    config = load_and_override_configs(TEST_CONFIG_PATHS)

    env_config = config['environment']
    environment: Env = build_object_within_registry_from_config(ENVIRONMENTS, env_config)
    algorithm_config = config['algorithm']
    algorithm = build_sb3_algorithm_from_config(environment, algorithm_config)

    roll_out_one_episode(environment, lambda obs: algorithm.predict(obs)[0])
    env_data: Environment = environment.export_environment_data()

    viz_prefix = f'/tmp/drltt-pytest-{generate_random_string(6)}'
    visualization_function = visualize_trajectory_tracking_episode
    visualization_function(env_data, viz_prefix)


if __name__ == '__main__':
    test_visualize_trajectory_tracking_episode()
