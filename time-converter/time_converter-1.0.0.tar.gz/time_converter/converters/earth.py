from time_converter import Converter
import datetime as dt
from numbers import Real
import calendar


class DatetimeConverter(Converter):
    def supports(self, unit=None, datatype=None):
        return (datatype is None or issubclass(datatype, dt.datetime)) and\
                   (unit is None or unit == 'dt' or unit == 'datetime')

    def convert_from_datetime(self, datetime):
        return datetime

    def convert_to_datetime(self, value):
        return value


class DoyConverter(Converter):
    def supports(self, unit=None, datatype=None):
        return (datatype is None or issubclass(datatype, tuple)) and (unit == 'doy')

    def convert_from_datetime(self, datetime):
        ttuple = datetime.utctimetuple()
        return ttuple.tm_year, \
               ttuple.tm_yday + ttuple.tm_hour / 24. + ttuple.tm_min / 24. / 60. + ttuple.tm_sec / 24. / 60. / 60.

    def convert_to_datetime(self, value):
        yy, day = value
        return dt.datetime(int(yy) - 1, 12, 31) + dt.timedelta(days=day)


class DecimalYearConverter(Converter):
    def supports(self, unit=None, datatype=None):
        return (datatype is None or issubclass(datatype, Real)) and (unit == 'dy' or unit == 'decimalyear')

    def convert_from_datetime(self, datetime):
        year_part = datetime - dt.datetime(year=datetime.year, month=1, day=1)
        year_length = dt.datetime(year=datetime.year + 1, month=1, day=1) - dt.datetime(year=datetime.year, month=1,
                                                                                        day=1)
        return datetime.year + year_part.total_seconds() / year_length.total_seconds()

    def convert_to_datetime(self, value):
        year = int(value)
        year_length = dt.datetime(year=year + 1, month=1, day=1) - dt.datetime(year=year, month=1, day=1)
        return dt.datetime(year, 1, 1) + dt.timedelta(seconds=year_length.total_seconds() * (value - year))


class PosixConverter(Converter):
    def supports(self, unit=None, datatype=None):
        return (datatype is None or issubclass(datatype, Real)) and (unit == 'posix')

    def convert_from_datetime(self, datetime):
        return calendar.timegm(datetime.utctimetuple())

    def convert_to_datetime(self, value):
        return dt.datetime.utcfromtimestamp(value)
