"""Project: Eskapade - A python-based package for data analysis.

Created: 2017/08/23

Description:
    Collection of helper functions to get fixtures, i.e. test data,
    ROOT/RooFit libs, and tutorials. These are mostly used by the
    (integration) tests.

Authors:
    KPMG Advanced Analytics & Big Data team, Amstelveen, The Netherlands

Redistribution and use in source and binary forms, with or without
modification, are permitted according to the terms listed in the file
LICENSE.
"""

import pathlib
import sys

from pkg_resources import resource_filename

import mongodbtools

# Configs that are shipped with eskapade.
_CONFIGS = {_.name: _ for _ in pathlib.Path(resource_filename(mongodbtools.__name__, 'config')).glob('**/*')}

# Resource types
_RESOURCES = {
    'config': _CONFIGS
}


def _resource(resource_type, name: str) -> str:
    """Return the full path filename of a resource.

    :param str resource_type: The type of the resource.
    :param str  name: The name of the resource.
    :returns: The full path filename of the fixture data set.
    :rtype: str
    :raises FileNotFoundError: If the resource cannot be found.
    """
    full_path = _RESOURCES[resource_type].get(name, None)

    if full_path and full_path.exists():
        return str(full_path)

    raise FileNotFoundError('Could not find {resource_type} "{name!s}"! Does it exist?'
                            .format(resource_type=resource_type, name=name))

def config(name: str) -> str:
    """Return the absolute path of a config.

    :param str name: The name of the config.
    :returns: The absolute path of the config.
    :raises FileNotFoundError: If the config cannot be found.
    """
    return _resource('config', name)
