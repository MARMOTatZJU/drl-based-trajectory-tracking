from typing import List, Tuple, Dict, Mapping
import os
import logging
import random
import string

import yaml
import numpy as np

from drltt_proto.sdk.exported_policy_test_case_pb2 import TensorFP
from drltt_proto.dynamics_model.basics_pb2 import DebugInfo

GLOBAL_DEBUG_INFO = DebugInfo()


def load_config_from_yaml(config_file: str) -> Dict:
    """Load config from yaml and handle exceptions.

    Args:
        config_file: Path to configuration file.
    """
    if not os.path.exists(config_file):
        raise FileNotFoundError(f'{config_file} does not exist')
    with open(config_file, 'r') as f:
        config = yaml.safe_load(f)
    logging.info(f'Loaded config from: {config_file}')

    return config


def save_config_to_yaml(config: Dict, config_file: str):
    """Save config to YAML file.

    Args:
        config: Config object to be saved.
        config_file: Path to YAML file.
    """
    with open(config_file, 'w') as f:
        yaml.dump(config, f)

    logging.info(f'Saved config at: {config_file}')


def convert_list_to_tuple_within_dict(
    dictionary: Dict,
    exceptions: Tuple[str] = tuple(),
) -> Dict:
    """Recursively cast list to tuple within a dict.

    Avoid modification issue (mutable / immutable). Support specified exception key.

    Also deal with some type issues.
    e.g. in case of stable-baselines3, https://github.com/DLR-RM/stable-baselines3/blob/v2.2.1/stable_baselines3/common/off_policy_algorithm.py#L157

    Args:
        dictionary: Dictionary to be processed.
        exceptions: Exceptional keys.

    Returns:
        Dict: Processed dictionary.
    """
    for k in tuple(dictionary.keys()):
        if k in exceptions:
            continue
        if isinstance(dictionary[k], List):
            dictionary[k] = tuple(dictionary[k])
        elif isinstance(dictionary[k], Mapping):
            dictionary[k] = convert_list_to_tuple_within_dict(
                dictionary[k],
                exceptions=exceptions,
            )
        else:
            continue

    return dictionary


def generate_random_string(n: int) -> str:
    """Generate a string with characters randomly chosen.

    Args:
        n: Desired length of string.

    Returns:
        str: Random string.
    """
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=n))


def override_config(
    base_config: Dict,
    update_config: Dict,
    allow_new_key: bool = False,
) -> Dict:
    """Override the value config.

    Args:
        base_config: Base config to be processed.
        update_config: Incremental config which contains key-value pair for overriding.
        allow_new_key: Whether allow creation of new key.

    Returns:
        Dict: The overridden config.
    """
    for k in tuple(update_config.keys()):
        if k not in base_config:
            if allow_new_key:
                base_config[k] = update_config[k]
            else:
                continue
        if type(base_config[k]) != type(update_config[k]):
            continue
        if isinstance(update_config[k], Dict):
            base_config[k] = override_config(
                base_config[k],
                update_config[k],
                allow_new_key=allow_new_key,
            )
        else:
            base_config[k] = update_config[k]

    return base_config


def load_and_override_configs(config_paths: List[str]) -> Dict:
    """Load and override a series of config files.

    Args:
        config_paths: The base config and the overriding configs.

            * The first config will serve as base config.
            * The rest configs will override the base config, respectively.

    Returns:
        Dict: The loaded and overridden config.
    """
    config = load_config_from_yaml(config_paths[0])

    for overriding_cfg_file in config_paths[1:]:
        overriding_config = load_config_from_yaml(overriding_cfg_file)
        override_config(config, overriding_config, allow_new_key=True)

    config = convert_list_to_tuple_within_dict(config)

    return config


def convert_numpy_to_TensorFP(arr: np.ndarray) -> TensorFP:
    """Convert numpy array to tensor proto.

    Args:
        arr: Numpy array to be converted.

    Returns:
        TensorFP: Converted tensor proto.
    """
    tensor_proto = TensorFP()
    tensor_proto.shape.extend(arr.shape)
    tensor_proto.data.extend(arr.reshape(-1))

    return tensor_proto


def convert_TensorFP_to_numpy(tensor_proto: TensorFP) -> np.ndarray:
    """Convert tensor proto to numpy array.

    Args:
        tensor_proto: Tensor proto.

    Returns:
        np.ndarray: Converted numpy array.
    """
    arr = np.array(tensor_proto.data).reshape(*tensor_proto.shape)

    return arr
