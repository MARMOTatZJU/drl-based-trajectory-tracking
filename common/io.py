from typing import Dict, Any
import os
from copy import deepcopy
import logging

import yaml


def load_config_from_yaml(config_file:str) -> Dict:
    """Load config from yaml and do exception handling"""
    if not os.path.exists(config_file):
        print(f'{config_file} does not exist')
        return None
    with open(config_file, 'r') as f:
        config = yaml.safe_load(f)
    logging.info(f'Loaded config at: {config_file}')

    return config
