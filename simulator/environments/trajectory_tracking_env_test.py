from gym import Env

from common import build_object_within_registry_from_config
from common.io import load_and_override_configs
from simulator import TEST_CONFIG_PATHS
from simulator.environments import ENVIRONMENTS


def test_trajectory_tracking_env():
    config = load_and_override_configs(TEST_CONFIG_PATHS)

    env_config = config['environment']

    env: Env = build_object_within_registry_from_config(ENVIRONMENTS, env_config)

    # observation, extra_info = env.reset()
    observation = env.reset()
    action = env.dynamics_model_manager.get_sampled_dynamics_model().get_action_space().sample()
    # observation, scalar_reward, terminated, truncated, extra_info = env.step(action)
    observation, scalar_reward, terminated, extra_info = env.step(action)


if __name__ == '__main__':
    test_trajectory_tracking_env()
