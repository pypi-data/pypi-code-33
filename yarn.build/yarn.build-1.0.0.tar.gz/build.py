# -*- coding: utf-8 -*-
"""zest.releaser plugin to build JavaScript projects"""
from six.moves.configparser import ConfigParser
from six.moves.configparser import NoSectionError
from six.moves.configparser import NoOptionError
from zest.releaser.utils import ask
from os.path import join
import logging
import os
import subprocess
import sys


LOGGER = logging.getLogger('yarn.build')


def get_configured_location(path):
    setup_cfg = os.sep.join([
        path,
        'setup.cfg'
    ])
    if os.path.exists(setup_cfg):
        config = ConfigParser()
        config.read(setup_cfg)
        try:
            folder_path = config.get('yarn.build', 'folder')
            if os.path.exists(folder_path):
                return folder_path
            logger.warning('{0} does not exist'.format(folder_path))
        except NoSectionError:
            pass
        except (NoOptionError, ValueError):
            LOGGER.warning(
                'No valid `folder` option found in `yarn.build` section '
                'within setup.cfg'
            )

    return None


def find_package_json(path):
    location = get_configured_location(path)
    if location:
        return location
    return recursive_find_package_json(path)


def recursive_find_package_json(path):
    """Find a ``packages.json`` file and run yarn on it"""
    for filename in os.listdir(path):
        dir_path = join(path, filename)
        if filename == 'package.json':
            LOGGER.info('yarn: package.json found!')
            return path
        elif os.path.isdir(dir_path):
            recursive_find_package_json(dir_path)

    return None


def build(path):
    """Build the JavaScript project at the given location"""
    LOGGER.debug('yarn: Compile dependencies')
    subprocess.call(['yarn', '--frozen-lockfile', ], cwd=path)
    LOGGER.debug('yarn: Build the project')
    subprocess.call(['yarn', 'run', 'release', ], cwd=path)


def build_project(data):
    """Build a JavaScript project from a zest.releaser tag directory"""
    tagdir = data.get('tagdir')
    if not tagdir:
        msg = 'yarn: no tagdir found in data.'
        LOGGER.warn(msg)
        return
    LOGGER.debug('yarn: Find and build JavaScript projects on {0}'.format(tagdir))
    try:
        location = find_package_json(tagdir)
        if location:
            build(location)
    except Exception:
        LOGGER.warn(
            'yarn: Building the project failed.',
            exc_info=True,
        )
        if data:
            # We were called as an entry point of zest.releaser.
            if not ask('Error building JS project. Do you want to continue?'):
                sys.exit(1)
