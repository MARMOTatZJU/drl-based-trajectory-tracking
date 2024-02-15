
from common.io import load_config_from_yaml
import numpy as np
from simulator.environments.trajectory_tracking_env import TrajectoryTrackingEnv


def test_trajectory_tracking_env():
    config_file = 'configs/trajectory_tracking/config-tiny-track.yaml'
    config = load_config_from_yaml(config_file)
    env_config = config['environment']
    env = TrajectoryTrackingEnv(**env_config)
    observation, extra_info = env.reset()
    action = env.dynamics_model_manager.get_sampled_dynamics_model().get_action_space().sample()
    observation, scalar_reward, terminated, truncated, extra_info = env.step(action)

if __name__ == '__main__':
    test_trajectory_tracking_env()
