import os
import sys

PACKAGE_DIR = os.path.dirname(__file__)
USR_LIB_DIR = f'{PACKAGE_DIR}/lib'
SDK_LIB_DIR = PACKAGE_DIR
sys.path.append(PACKAGE_DIR)


from .trajectory_tracker import TrajectoryTracker

__all__ = [
    'TrajectoryTracker',
]
