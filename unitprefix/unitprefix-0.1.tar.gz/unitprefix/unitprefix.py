# -*- coding: utf-8 -*-
import six
from math import pow

# Format for value unit representation
_FORMAT = "{value} {unit}"

# Unit sytems; For now SI only supported. We will add support for NIST system for bit
SI = int(10)  # SI system have radix 10
NIST = int(2)  # NIST system have radix 2

# SI (International System Of Units) prefix having radix 10
_SI_PREFIX = {
    u"y": -24,
    u"z": -21,
    u"a": -18,
    u"f": -15,
    u"p": -12,
    u"n": -9,
    u"u": -6,
    u"m": -3,
    u"c": -2,
    u"d": -1,
    u"": 0,
    u"da": 1,
    u"h": 2,
    u"k": 3,
    u"M": 6,
    u"G": 9,
    u"T": 12,
    u"P": 15,
    u"E": 18,
    u"Z": 21,
    u"Y": 24,
}


class UnitPrefix(object):
    """ Base class for all Unit Prefix conversions

    Args:
        value(int, float, long): Conversing value
        unit(str): Conversing unit
        prefix(str): prefix of (SI/NIST) sytem unit
        system: UnitPrefix.SI/ UnitPrefix.NIST
    """

    def __init__(self, value=0, unit=None, base_value=None, base_unit=None, prefix=None, system=SI):
        self.value = value
        self.unit = unit
        self.base_value = base_value
        self.base_unit = base_unit
        self.prefix = prefix
        self.system = system

        if not self.prefix and self.unit:
            for prefix, multi in _SI_PREFIX.items():
                if prefix == self.unit[0]:
                    self.prefix = prefix
                    self.base_value = self.value * pow(self.system, multi)
                    self.base_unit = self.unit[1:]
                    break
            else:
                self.base_unit = unit
                self.base_value = self.value
        elif self.prefix and not self.unit:
            self.base_unit = ""
            self.base_value = self.value
        else:
            raise ValueError("No prefix and unit provided")

        for p, mult in _SI_PREFIX.items():
            unit = "{}{}".format(p, self.base_unit)
            _method = self._make_method(prefix=p, unit=unit)
            setattr(self, unit, _method)

    def _make_method(self, prefix, unit):
        def _method():
            value = self.base_value * pow(self.system, -_SI_PREFIX[prefix])
            return UnitPrefix(value=value, unit=unit)
        return _method

    def __repr__(self):
        return _FORMAT.format(value=self.value, unit=self.unit)


def parse_value_unit(data, system=SI):
    """ Take string with value and unit. parse string and display all available options

    Args:
        data (str): value and unit string
    """
    # Check for string or unicode data
    if not isinstance(data, six.string_types):
        raise ValueError("{} is not string/ unicode type data".format(str(data)))

    # seperate value and unit
    try:
        index = list([item.isalpha() for item in data]).index(True)
    except ValueError:
        raise ValueError("Unit not found")

    value, unit = float(data[:index]), data[index:]
    return UnitPrefix(value=value, unit=unit, system=system)
