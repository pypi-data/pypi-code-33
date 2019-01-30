# flake8: noqa
from __future__ import absolute_import, division, print_function

try:
    from sumeru import *
except ImportError:
    msg = ("Dask's sumeru scheduler is not installed.\n\n"
           "Please either conda or pip install dask sumeru:\n\n"
           "  conda install dask sumeru          # either conda install\n"
           "  pip install dask sumeru --upgrade  # or pip install")
    raise ImportError(msg)
