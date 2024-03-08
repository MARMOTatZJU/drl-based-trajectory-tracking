from typing import List, Tuple, Union
from enum import Enum
import os

from . import PACKAGE_DIR, USR_LIB_DIR, SDK_LIB_DIR

CHECKPOINT_DIR = f'{PACKAGE_DIR}/checkpoint/'

from export_symbols import (
    TrajectoryTracker as ExportedTrajectoryTracker,
    trajectory_tracker_set_reference_line,
    trajectory_tracker_set_dynamics_model_initial_state,
    trajectory_tracker_track_reference_line,
)


class DynamicsModelType(Enum):
    """Vechicle type.

    See `./configs/trajectory_tracking/config-track-base.yaml` for definition
    """

    SHORT_VEHICLE: int = 0
    LONG_VEHICLE: int = 1
    MIDDLE_VEHICLE: int = 2


class TrajectoryTracker:
    """DRLTT Trajectory Tracking policy wrapper"""

    def __init__(self, vehicle_type: int = DynamicsModelType.SHORT_VEHICLE.value):
        """
        Args:
            vehicle_type: Vehicle type. Default is short vehicle.
        """
        self._tracker = ExportedTrajectoryTracker(CHECKPOINT_DIR, vehicle_type)

    def track_traference_line(
        self,
        reference_line: List[Tuple[float, float]],
        init_state: Union[Tuple[float, float, float, float], None] = None,
    ) -> Tuple[List[Tuple[float, float, float, float]], List[Tuple[float, float]]]:
        """Track a reference line with the underlying policy model.

        Nomenclature:

        - x: X-coordinate in [m] within (-inf, +inf)
        - y: Y-coordinate in [m] within (-inf, +inf)
        - r: heading in [rad] within [-pi, pi), following convention of math lib like `std::atan2`
        - v: scalar speed in [m/s] within [0, +inf)

        Args:
            reference_line: Reference line, format=List[<x, y>].
            init_state: Initial state, format=<x, y, r, v>.

        Return:
            Tuple[states, action]: The tracked trajectory. All elements have the same length
                that is equal to the length of reference line.

                - The first element is a sequence of states.
                - The second element is a sequence of actions.
        """
        trajectory_tracker_set_reference_line(self._tracker, reference_line)
        if init_state is not None:
            trajectory_tracker_set_dynamics_model_initial_state(self._tracker, init_state)
        rt_states, rt_actions, rt_observations = trajectory_tracker_track_reference_line(self._tracker)

        return rt_states, rt_actions
