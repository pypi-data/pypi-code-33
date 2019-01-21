# -*- coding: utf-8 -*-
"""Universal converter for time units. Usage:

.. code:: python

    from time_converter import Time
    Time(1000, 'sol').to('datetime')

Currently supported units:

- ``'datetime', 'dt'``: Python datetime objects
- ``'sol'``: MSL sol numbers (float)
- ``'sclk'``: MSL spacecraft clock (float)
- ``'doy'``: Tuple of (year, doy) (year: int, doy: float)
- ``'decimalyear', 'dy'``: Decimal year (float, e.g. 2018.086)
- ``'posix'``: POSIX timestamp (seconds since Jan 1 1970, 00:00 UTC)

Providing the unit name is optional for converting from datetime as it can be inferred from the data type, e.g.

.. code:: python

    from time_converter import Time
    import datetime as dt
    Time(dt.datetime(2018, 1, 1)).to('sol')

Author: Johan von Forstner <forstner@physik.uni-kiel.de>, January 2018
"""

import datetime as dt
from abc import ABCMeta, abstractmethod

try:
    import pandas as pd
except:
    pd = None

import numpy as np
from six import with_metaclass


class Converter(with_metaclass(ABCMeta)):
    """
    Abstract class that defines a converter for converting between some time unit <-> Python's datetime class
    """

    @abstractmethod
    def supports(self, unit=None, datatype=None):
        # type: (str, type) -> bool
        """
        Determines if this converter can convert to or from the given data type

        :param unit: string description of the unit supplied by the user, can be None when not supplied
        :param datatype: class of the data that is supplied (e.g. float, datetime, ...) to convert from, or None
        """
        pass

    @abstractmethod
    def convert_from_datetime(self, datetime):
        # type: (dt.datetime) -> object
        """
        Converts the given datetime value to the unit supported by this converter

        :param datetime: datetime value
        """
        pass

    @abstractmethod
    def convert_to_datetime(self, value):
        # type: (object) -> dt.datetime
        """
        Converts the given value from the unit supported by this converter to a datetime value

        :param value:
        """
        pass


from time_converter.converters.earth import *
from time_converter.converters.msl import *


class Time:
    converters = [clazz() for clazz in Converter.__subclasses__()]  # instantiate one converter of every kind

    def __init__(self, value, unit=None):
        if self._is_list(value):
            if len(value) == 0:
                self.dt = []
            else:
                converter = self._get_converter(unit, type(value[0]))
                self.dt = [converter.convert_to_datetime(val) for val in value]
            self.original_value = value
        else:
            converter = self._get_converter(unit, type(value))
            self.dt = converter.convert_to_datetime(value)

    def to(self, unit):
        converter = self._get_converter(unit)
        if self._is_list(self.dt):
            arr = np.array([converter.convert_from_datetime(d) for d in self.dt])
            if pd is not None and type(self.original_value) == pd.core.series.Series:
                return pd.Series(arr, index=self.original_value.index)
            else:
                return arr
        else:
            return converter.convert_from_datetime(self.dt)

    def _get_converter(self, unit, datatype=None):
        for converter in self.converters:
            if converter.supports(unit, datatype):
                return converter

        raise ValueError('unknown unit {} or unsupported type {}'.format(unit, datatype))

    def _is_list(self, value):
        return type(value) in [np.ndarray, list] or pd is not None and type(value) == pd.core.series.Series
