"""A haidata demonstration vehicle.

.. moduleauthor:: Hans Roggeman <hansroggeman2@gmail.com>

"""
__version__ = '0.0.2'

import pandas as pd
import numpy as np
import os

from .haidatautils import *
from .haidatacfg import *

from .drop_cols import *
from .fix_colnames import *
from .fix_empty_cols import *
from .fix_encode import *
from .fix_excess_stdev import *
from .to_datetime import *
from .turn_to_int import *

myPath = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, myPath)
sys.path.insert(0, os.path.join(myPath, 'config'))
sys.path.insert(0, os.path.join(myPath, 'tests'))


def start():
    # "This starts this module running ..."
    pass
