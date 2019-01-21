from time_converter import Converter

from . import chronos
import datetime as dt
from numbers import Real

SOL = 88775.24409  # seconds per sol
LANDING = dt.datetime(2012, 8, 5, 13, 49, 59)


class SolConverter(Converter):
    def supports(self, unit=None, datatype=None):
        return (datatype is None or issubclass(datatype, Real)) and (unit == 'sol')

    def convert_from_datetime(self, datetime):
        return (datetime - LANDING).total_seconds() / SOL

    def convert_to_datetime(self, value):
        return LANDING + dt.timedelta(seconds=value * SOL)


class SclkConverter(Converter):
    def supports(self, unit=None, datatype=None):
        return (datatype is None or issubclass(datatype, Real)) and (unit == 'sclk')

    def convert_from_datetime(self, datetime):
        return chronos.dt_to_sclk(datetime)

    def convert_to_datetime(self, value):
        return chronos.sclk_to_dt(value)
