# -*- coding: utf-8 -*-

import os
if 'MPLBACKEND' not in os.environ:
    os.environ['MPLBACKEND'] = 'Agg'

from .baseclasses import GeoArray  # noqa: E402
from .masks import BadDataMask  # noqa: E402
from .masks import NoDataMask  # noqa: E402
from .masks import CloudMask  # noqa: E402

from .version import __version__, __versionalias__   # noqa (E402 + F401)


__author__ = """Daniel Scheffler"""
__email__ = 'danschef@gfz-potsdam.de'
__all__ = ['__version__',
           '__versionalias__',
           '__author__',
           '__email__',
           'GeoArray',
           'BadDataMask',
           'NoDataMask',
           'CloudMask'
           ]
