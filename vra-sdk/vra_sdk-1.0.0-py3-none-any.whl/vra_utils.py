# -*- coding: utf-8 -*-
import os
import re
import sys
import json
from pathlib import Path
import importlib
import time
from vra_sdk.vra_exceptions import VraSdkUtilsException, VraSdkConfigException


def resolve_path(config_path):
    """Return the absolute path of a file
    
    Args:
        config_path (string): absolute or relative path to a file
    
    Returns:
        string: path to the config_path file
    """

    return os.path.abspath(os.path.join(os.getcwd(), config_path))


def prettify_key(initial_dict):
    """transform camelCase dict key to snake_case
    
    Args:
        dict (dict): dict to transform key of
    
    Returns:
        dict: transformed dict
    """

    dict_clean = {}
    for key, value in initial_dict.items():
        dict_clean[to_snake_case(key)] = value
    return dict_clean


def to_snake_case(name):
    """transform CamelCase string to snake_case
    
    Args:
        name (string): string to convert
    
    Returns:
        string: converted string
    """

    s1 = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', name)
    return re.sub('([a-z0-9])([A-Z])', r'\1_\2', s1).lower()



def get_module_class(kls):
    """Provide module and class from a string
    
    Args:
        kls (string): path to the module
    
    Returns:
        tuple: tuple of module, class
    """

    mod, _, cls = kls.rpartition('.')
    mod = importlib.import_module(mod)

    return mod, getattr(mod, cls)


def clean_kwargs_key(**kwargs):
    """replace dot (.) to underscore for kwargs key
    
    Returns:
        dict: transformed kwargs
    """

    cleaned_kwargs = {k.replace('.', '_'): v for (k, v) in kwargs.items()}
    return cleaned_kwargs


def load_payload_file(payload_path):
    """load json file
    
    Args:
        payload_path (string): path to the json file
    
    Returns:
        dict: serialization of the json file
    """

    try:
        with open(resolve_path(payload_path)) as f:
            base = json.load(f)
        return base
    except FileNotFoundError as e:
        raise VraSdkConfigException(
            f'Error opening payload {payload_path}. Does the file exist?: {e}')
    except Exception as e:
        raise VraSdkUtilsException(
            f'Unmanaged error during payload loading for payload {payload_path}: {e}')
