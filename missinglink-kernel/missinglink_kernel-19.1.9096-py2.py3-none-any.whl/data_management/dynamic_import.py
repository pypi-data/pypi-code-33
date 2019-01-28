# -*- coding: utf8 -*-
import logging
import sys
import threading

import pkg_resources
from pkg_resources import VersionConflict, DistributionNotFound, UnknownExtra

COMMON_DEPENDENCIES = [
    'ml-legit>=18.12.1107',
    'diskcache>=3.0.1',
]

GCS_DEPENDENCIES = [
    'google-cloud-storage==1.6.0',
]
S3_DEPENDENCIES = [
    'boto3>=1.4.8,<1.5.0',
]

KEYWORDS = []


__pip_install_lock = threading.Lock()


def __in_venv():
    if hasattr(sys, 'real_prefix'):
        # virtualenv venvs
        result = True
    else:
        # PEP 405 venvs
        result = sys.prefix != getattr(sys, 'base_prefix', sys.prefix)

    return result


def install_dependencies(dependencies, throw_exception=True):
    from missinglink.sdk.pip_util import pip_install

    running_under_virtualenv = __in_venv()

    needed_dependencies = []
    for requirement in dependencies:
        if _is_dependency_installed(requirement):
            continue

        needed_dependencies += [requirement]

    if not needed_dependencies:
        return

    with __pip_install_lock:
        p, args = pip_install(None, needed_dependencies, not running_under_virtualenv)

        if p is None:
            raise Exception('Failed to install requirement: %s' % needed_dependencies)

        try:
            std_output, std_err = p.communicate()
        except Exception:
            if throw_exception:
                raise

            logging.exception('%s failed', ' '.join(args))
            return False

        rc = p.returncode

        if rc != 0:
            logging.error('Failed to install requirement: %s' % needed_dependencies)
            logging.error('Failed to run %s (%s)\n%s\n%s', ' '.join(args), rc, std_err, std_output)

            if throw_exception:
                raise Exception('Failed to install requirement: %s' % needed_dependencies)

        logging.info('install requirement: %s' % needed_dependencies)
        logging.info('ran %s (%s)\n%s\n%s', ' '.join(args), rc, std_err, std_output)


def _is_dependency_installed(requirement):
    try:
        pkg_resources.require(requirement)
    except (DistributionNotFound, ) as ex:
        logging.debug('Error when checking if %s is installed "%s"', requirement, ex)
        return False
    except (IOError, VersionConflict, UnknownExtra) as ex:
        logging.warning('Error when checking if %s is installed "%s"', requirement, ex)
        return False

    return True
