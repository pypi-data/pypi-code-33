"""
limis core module

Provides solution wide functionality for managing logging, settings, applications, etc.
"""
from distutils.version import StrictVersion

from limis import VERSION


def get_version() -> str:
    """
    Retrieves the version of this module.

    :return: String with the strict current version
    """
    return str(StrictVersion('.'.join(map(str, VERSION))))
