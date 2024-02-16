from typing import List, Tuple, Dict, Mapping
import os
import logging

import yaml


def load_config_from_yaml(config_file: str) -> Dict:
    """Load config from yaml and do exception handling"""
    if not os.path.exists(config_file):
        logging.warn(f'{config_file} does not exist')
        return None
    with open(config_file, 'r') as f:
        config = yaml.safe_load(f)
    logging.info(f'Loaded config at: {config_file}')

    return config


def convert_list_to_tuple_within_dict(
    dictionary: Dict,
    exceptions: Tuple[str] = tuple(),
):
    """Recursively cast list to tuple within a dict

    Avoid modification issue (mutable / immutable)
    Support specified exception key

    Also deal with some type issues
    e.g. in case of stable-baselines3,
        https://github.com/DLR-RM/stable-baselines3/blob/v2.2.1/stable_baselines3/common/off_policy_algorithm.py#L157
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
