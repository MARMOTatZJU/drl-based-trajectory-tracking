from typing import Union

import numpy as np


def normalize_angle(angle: Union[float, np.ndarray]) -> Union[float, np.ndarray]:
    """Normalize angle to [-pi, pi), compatible with Numpy vectorization.

    Args:
        angle: Angle to be normalized.

    Returns:
        Normalized angle.

    """
    return (angle + np.pi) % (2 * np.pi) - np.pi


# TODO: use screw theory to refactor this part
def transform_points(points: np.ndarray, transform_matrix: np.ndarray) -> np.ndarray:
    """Transform 2-D points with transform matrix.

    Args:
        points: Points to be transformed, shape=(N, 2).
        transform_matrix: trnasform_matrix which lies in group SO(2), shape=(3, 3).

    Returns:
        np.ndarray: Transformed points, shape=(N, 2).
    """
    points = np.concatenate([points, np.ones((points.shape[0], 1))], axis=1)
    points = transform_matrix @ points.T
    points = points.T
    points = points[:, :2]

    return points


def transform_between_local_and_world(points: np.ndarray, body_state: np.ndarray, trans_dir: str) -> np.ndarray:
    points, body_state = points.copy(), body_state.copy()
    x, y, r = body_state[:3]

    translation_matrix = np.array(
        (
            (1.0, 0.0, -x),
            (0.0, 1.0, -y),
            (0.0, 0.0, 1.0),
        )
    )
    rotation_matrix = np.array(
        (
            (np.cos(r), np.sin(r), 0.0),
            (-np.sin(r), np.cos(r), 0.0),
            (0.0, 0.0, 1.0),
        )
    )
    if trans_dir == 'world_to_local':
        transform_matrix = rotation_matrix @ translation_matrix
    elif trans_dir == 'local_to_world':
        transform_matrix = np.linalg.inv(rotation_matrix @ translation_matrix)
    else:
        raise ValueError(f'Unknown transform direction: {trans_dir}')

    transformed_points = transform_points(points, transform_matrix)

    return transformed_points


def transform_to_local_from_world(points: np.ndarray, body_state: np.ndarray) -> np.ndarray:
    return transform_between_local_and_world(
        points,
        body_state,
        trans_dir='world_to_local',
    )


def transform_to_world_from_local(points: np.ndarray, body_state: np.ndarray) -> np.ndarray:
    return transform_between_local_and_world(
        points,
        body_state,
        trans_dir='local_to_world',
    )
