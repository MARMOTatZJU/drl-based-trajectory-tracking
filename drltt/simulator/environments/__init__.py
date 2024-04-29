from common import Registry

ENVIRONMENTS = Registry()

from .env_interface import CustomizedEnvInterface
from .trajectory_tracking_env import TrajectoryTrackingEnv
from .env_interface import ExtendedGymEnv

__all__ = [
    'TrajectoryTrackingEnv',
    'CustomizedEnvInterface',
    'ExtendedGymEnv',
]
