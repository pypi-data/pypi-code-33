# -*- coding: utf-8 -*-
"""objects
"""

from .dataobject import DataObject

from pkg_resources import get_distribution, DistributionNotFound

try:
    # Change here if project is renamed and does not equal the package name
    DIST_NAME = __name__
    __version__ = get_distribution(DIST_NAME).version
except DistributionNotFound:
    __version__ = 'unknown'
