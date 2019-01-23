import logging
import warnings
from datetime import timedelta

from dateutil import parser

from pyinfluxdb.client import InfluxClient

logger = logging.getLogger(__name__)

__all__ = ['InfluxClient']


def time_to_local(time_in):
    warnings.warn("deprecated", DeprecationWarning)
    time = parser.parse(time_in)
    time_local = time + timedelta(hours=-8)
    time_out = time_local.strftime('%Y-%m-%d %H:%M:%S')
    return time_out
