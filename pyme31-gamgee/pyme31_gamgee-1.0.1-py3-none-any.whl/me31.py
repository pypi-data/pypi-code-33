import serial
from serial import *
from time import sleep
from measurment import MeasuringMode, Unit, Measurment, measuring_mode_strings, unit_strings

class Me31OverloadError(Exception):
    pass


class Me31(object):
    # timeout for the serial connection
    _timeout = 1

    # the baudrate is fixed to 600 baud
    _baudrate = 600

    # the handler for the serial connection
    _connection_handler = None

    def __init__(self, comport):
        if type(comport) != str:
            raise ValueError("comport must be of type str")
        
        self._connection_handler = serial.Serial(comport, 600, timeout=self._timeout, stopbits=STOPBITS_TWO,
                                                     bytesize=SEVENBITS)

        self._connection_handler.setRTS(False)
        self._connection_handler.setDTR(True)
        self._connection_handler.read()

    # makes sure the serial connection gets closed on exit
    def __del__(self):
        if type(self._connection_handler) is serial.Serial:
            self._connection_handler.close()

    def _request_value(self):
        # to read the current value from the meter we have to request it first by sending 'd' (0x44)
        self._connection_handler.write(str.encode('d'))

    def _read_raw_data(self):
        self._request_value()
        # not sure what the best value for the timeout is. 0.5 sec seems to be to short...
        sleep(1)
        # the dmm returns 14 bytes
        value = self._connection_handler.read(14)

        if len(value) == 0:
            raise ValueError("no reponse")
        elif (len(value) != 14):
            raise ValueError("expected {0} bytes, got {1}".format(14, len(value)))

        return value[:-1]

    def _get_range(self, raw_string):
        range_string = raw_string[9:13].strip()

        # possible range strings: mV, V, Ohm, kOhm, MOhm, mA, A

        if range_string == str.encode(unit_strings[Unit.MILIVOLT]):
            return Unit.MILIVOLT
        elif range_string == str.encode(unit_strings[Unit.VOLT]):
            return Unit.VOLT
        elif range_string == str.encode(unit_strings[Unit.OHM]):
            return Unit.OHM
        elif range_string == str.encode(unit_strings[Unit.KILOOHM]):
            return Unit.KILOOHM
        elif range_string == str.encode(unit_strings[Unit.MEGAOHM]):
            return Unit.MEGAOHM
        elif range_string == str.encode(unit_strings[Unit.MILIAMPERE]):
            return Unit.MILIAMPERE
        elif range_string == str.encode(unit_strings[Unit.AMPERE]):
            return Unit.AMPERE
        else:
            raise NotImplementedError()

    def _get_measuring_mode(self, raw_string):
        measuring_mode_string = raw_string[0:2].strip()

        # possible measuring mode strings: DC, AC, OH, DI

        if measuring_mode_string == str.encode('DC'):
            return MeasuringMode.DC
        elif measuring_mode_string == str.encode('AC'):
            return MeasuringMode.AC
        elif measuring_mode_string == str.encode('OH'):
            return MeasuringMode.OHM
        elif measuring_mode_string == str.encode('DI'):
            return MeasuringMode.DIODE
        else:
            raise NotImplementedError()

    def _get_value(self, raw_string):
        value_string = raw_string[3:9].strip()

        if value_string.endswith(str.encode('L')):
            raise Me31OverloadError

        return float(value_string)

    def get_measurment(self):
        raw_string = self._read_raw_data()
        measurment_mode = self._get_measuring_mode(raw_string)
        overload = False
        try:
            value = self._get_value(raw_string)
        except Me31OverloadError:
            value = float(0.0)
            overload = True
        unit = self._get_range(raw_string)
        return Measurment(measurment_mode, value, unit, overload)

    def get_current_range(self):
        return self._get_range(self._read_raw_data())

    def get_measuring_current_mode(self):
        return self._get_measuring_mode(self._read_raw_data())

    def get_value(self):
      return self._get_value(self._read_raw_data())
