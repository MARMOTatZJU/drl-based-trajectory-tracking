from typing import Dict, Any
import os
from copy import deepcopy
import logging

import yaml
from frozendict import frozendict


def get_object_by_name_from_registry(registry: Dict[str, Any], name: str) -> object:
    if name not in registry:
        raise ValueError(f'Object {name} does not exist')

    return registry[name]


def build_object_by_config_from_registry(registry: Dict[str, Any], config: Dict[str, Any]=frozendict(), **kwargs) -> object:
    config = deepcopy(config)
    config = dict(**config)
    kwargs = deepcopy(kwargs)
    config.update(kwargs)
    class_name = config.pop('type')
    class_object = get_object_by_name_from_registry(
        registry,
        class_name,
    )
    built_object = class_object(**config)

    return built_object


def load_config_from_yaml(config_file:str) -> Dict:
    """Load config from yaml and do exception handling"""
    if not os.path.exists(config_file):
        print(f'{config_file} does not exist')
        return None
    with open(config_file, 'r') as f:
        config = yaml.safe_load(f)
    logging.info(f'Loaded config at: {config_file}')

    return config
