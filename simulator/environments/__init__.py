from common import Registry

ENVIRONMENTS = Registry()

from .trajectory_tracking_env import TrajectoryTrackingEnv

__all__ = [
    'TrajectoryTrackingEnv',
]
