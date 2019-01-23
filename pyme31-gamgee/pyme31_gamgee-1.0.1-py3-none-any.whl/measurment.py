from enum import Enum


class MeasuringMode(Enum):
    DC = 1
    AC = 2
    OHM = 3
    DIODE = 4


measuring_mode_strings = {MeasuringMode.DC: "DC", MeasuringMode.AC: "AC", MeasuringMode.OHM: "Ohm",
                          MeasuringMode.DIODE: "Diode"}


class Unit(Enum):
    MILIVOLT = 1
    VOLT = 2
    OHM = 3
    KILOOHM = 4
    MEGAOHM = 5
    MILIAMPERE = 6
    AMPERE = 7


unit_strings = {Unit.MILIVOLT: "mV", Unit.VOLT: "V", Unit.OHM: "Ohm", Unit.KILOOHM: "kOhm", Unit.MEGAOHM: "MOhm",
                Unit.MILIAMPERE: "mA", Unit.AMPERE: "A"}

class Measurment():

    @property
    def measuring_mode(self):
        return self._measuring_mode

    @property
    def value(self):
        return self._value

    @property
    def unit(self):
        return self._unit

    @property
    def overload(self):
        return self._overload

    def __str__(self):
        if self.overload:
            return "Overload"
        return "{0} {1} {2}".format(measuring_mode_strings[self.measuring_mode], self.value, unit_strings[self.unit])

    def __init__(self, measuring_mode, value, unit, overload = False):
        if type(measuring_mode) != MeasuringMode:
            raise TypeError
        if type(unit) != Unit:
            raise TypeError

        self._measuring_mode = measuring_mode
        self._value = value
        self._unit = unit
        self._overload = overload