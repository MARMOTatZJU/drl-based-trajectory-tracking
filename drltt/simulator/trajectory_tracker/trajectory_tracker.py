from typing import List, Tuple, Union

import numpy as np
import torch

from drltt.simulator.environments.trajectory_tracking_env import TrajectoryTrackingEnv
from drltt.simulator.rl_learning.sb3_utils import roll_out_one_episode
from drltt.simulator.trajectory.reference_line import ReferenceLineManager

from drltt_proto.environment.environment_pb2 import Environment
from drltt_proto.trajectory.trajectory_pb2 import ReferenceLine


class TrajectoryTracker:
    """Trajectory tracking SDK class"""

    def __init__(self, checkpoint_dir: str):
        """
        Args:
            checkpoint_dir: Path to the checkpoint's directory.
        """
        self.policy = torch.jit.load(f'{checkpoint_dir}/traced_policy.pt')
        env_info = Environment()
        with open(f'{checkpoint_dir}/env_data.bin', 'rb') as f:
            env_info.ParseFromString(f.read())
        self.env = TrajectoryTrackingEnv(env_info=env_info)

    def track_reference_line(
        self,
        init_state: Union[Tuple[float, float, float, float], None] = None,
        dynamics_model_name: Union[str, None] = 'ShortVehicle',
        reference_line: Union[List[Tuple[float, float]], None] = None,
    ) -> Tuple[List[Tuple[float, float, float, float]], List[Tuple[float, float]]]:
        """Track a reference line with the underlying policy model.

        Nomenclature:

        - x: X-coordinate in [m] within (-inf, +inf)
        - y: Y-coordinate in [m] within (-inf, +inf)
        - r: heading in [rad] within [-pi, pi), following convention of math lib like `std::atan2`
        - v: scalar speed in [m/s] within [0, +inf)

        TODO: refer this part to definition of prototype and so for avoid redundant documentation.

        Args:
            init_state: Initial state, format=<x, y, r, v>.
            dynamics_model_name: Name of the dynamics model.
            reference_line: Reference line, format=List[<x, y>].

        Return:
            Tuple[states, action]: The tracked trajectory. All elements have the same length
                that is equal to the length of reference line.

                - The first element is a sequence of states.
                - The second element is a sequence of actions.
        """
        if init_state is not None:
            init_state = np.array(init_state)
        if reference_line is not None:
            reference_line: ReferenceLine = ReferenceLineManager.np_array_to_reference_line(np.array(reference_line))

        states, actions, observations = roll_out_one_episode(
            self.env,
            self.policy_func,
            init_state=init_state,
            dynamics_model_name=dynamics_model_name,
            reference_line=reference_line,
        )
        return (
            [tuple(state) for state in states],
            [tuple(action) for action in actions],
        )

    def policy_func(self, observation: np.ndarray) -> np.ndarray:
        """Wrapper of underlying JIT policy in form of func(observation) -> action.

        Including preprocessing and post processing of the tensor.

        Args:
            observation: Observation.

        Returns:
            np.ndarray: Action.
        """
        observation_tensor = torch.from_numpy(observation).reshape(1, -1)
        action_tensor = self.policy(observation_tensor)
        action = action_tensor.reshape(-1).numpy()

        return action

    def get_step_interval(self) -> float:
        """Get the step interval in time.

        Returns:
            float: Time step interval.
        """
        return self.env.env_info.trajectory_tracking.hyper_parameter.step_interval

    def get_dynamics_model_info(self) -> str:
        """Get the string for the information of dynamics models.

        Returns:
            str: Pretty string containing information of dynamics models.
        """
        return self.env.get_dynamics_model_info()

    def get_reference_line(self) -> List[Tuple[float, float]]:
        """Get the current reference line.

        Returns:
            List[Tuple[float, float]]: Reference line, shape=[<x, y>].
        """
        arr = ReferenceLineManager.reference_line_to_np_array(self.env.get_reference_line())

        return [tuple(waypoint) for waypoint in arr]
