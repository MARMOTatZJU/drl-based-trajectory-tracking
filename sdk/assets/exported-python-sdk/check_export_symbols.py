import numpy as np

from export_symbols import (
    TrajectoryTracker,
    trajectory_tracker_set_reference_line,
    trajectory_tracker_set_dynamics_model_initial_state,
    trajectory_tracker_track_reference_line,
)
from drltt_proto.environment.environment_pb2 import Environment


def main():
    env_data = Environment()
    with open('./checkpoint/env_data.bin', 'rb') as f:
        env_data.ParseFromString(f.read())

    reference_line = [
        (waypoint.x, waypoint.y)
        for waypoint in env_data.trajectory_tracking.episode.reference_line.waypoints[
            : env_data.trajectory_tracking.episode.tracking_length
        ]
    ]
    init_state_proto = env_data.trajectory_tracking.episode.dynamics_model.states[0]
    init_state = (
        init_state_proto.bicycle_model.body_state.x,
        init_state_proto.bicycle_model.body_state.y,
        init_state_proto.bicycle_model.body_state.r,
        init_state_proto.bicycle_model.v,
    )
    tracker = TrajectoryTracker('./checkpoint/', env_data.trajectory_tracking.episode.selected_dynamics_model_index)
    trajectory_tracker_set_reference_line(tracker, reference_line)
    trajectory_tracker_set_dynamics_model_initial_state(tracker, init_state)
    rt_states, rt_actions, rt_observations, rt_debug_datas = trajectory_tracker_track_reference_line(tracker)

    print('state shape: ', np.array(rt_states).shape)
    print('action shape: ', np.array(rt_actions).shape)
    print('observation shape: ', np.array(rt_observations).shape)

    gt_states = list()
    for state in env_data.trajectory_tracking.episode.dynamics_model.states:
        gt_state = (
            state.bicycle_model.body_state.x,
            state.bicycle_model.body_state.y,
            state.bicycle_model.body_state.r,
            state.bicycle_model.v,
        )
        gt_states.append(gt_state)

    gt_actions = list()
    for action in env_data.trajectory_tracking.episode.dynamics_model.actions:
        gt_action = (
            action.bicycle_model.a,
            action.bicycle_model.s,
        )
        gt_actions.append(gt_action)

    gt_observations = list()
    for observation in env_data.trajectory_tracking.episode.dynamics_model.observations:
        gt_observation = tuple(observation.bicycle_model.feature)
        gt_observations.append(gt_observation)

    state_diffs = np.array(gt_states, dtype=np.float32) - np.array(rt_states, dtype=np.float32)
    print(f'state max diff: {state_diffs.max()}')

    action_diffs = np.array(gt_actions, dtype=np.float32) - np.array(rt_actions, dtype=np.float32)
    print(f'action max diff: {action_diffs.max()}')

    observation_diffs = np.array(gt_observations, dtype=np.float32) - np.array(rt_observations, dtype=np.float32)
    print(f'observation max diff: {observation_diffs.max()}')


if __name__ == '__main__':
    main()
