from iotile.core.hw.proxy.proxy import TileBusProxyObject
from iotile.core.hw.exceptions import *
from iotile.core.utilities.console import ProgressBar
import struct
from iotile.core.utilities.intelhex import IntelHex
from time import sleep
from iotile.core.utilities.typedargs.annotate import annotated,param,return_type, context
from iotile.core.utilities.typedargs import iprint
from iotile.core.utilities import typedargs
from itertools import product
from iotile.core.exceptions import *
import math

@context("GPIOProxy")
class GPIOProxy (TileBusProxyObject):
    """
    Provide access to GPIO tile functionality


    :param stream: CMDStream instance that can communicate with this tile
    :param addr: Local tilebus address of this tile
    """

    @classmethod
    def ModuleName(cls):
        return 'gpio1 '

    def __init__(self, stream, addr):
        super(GPIOProxy, self).__init__(stream, addr)

    @return_type('integer')
    @param("channel", "integer", desc="Pulsecounting channel to be queried [0-7]")
    def relative_pulsecount(self, channel):
        """Get the number of pulses seen since the last time this rpc was called

        :param: channel: The channel that should be fetched
        :rtype: integer
        """
        reading, = self.rpc(0x80, 0x00 + channel, result_format="L")
        return reading


    @return_type('integer')
    def get_rtctime(self):
        time, = self.rpc(0xab, 0x07, result_format="L")
        return time

    @return_type('float')
    @param('channel', 'integer', desc="Channel to query")
    def get_pulserate(self, channel):
        """
        Get the current estimate of the pulse rate in pulses per minute.

        :rtype: float
        """
        reading, = self.rpc(0x80, 0x10 + channel, result_format="L")
        
        if reading == 0:
            return 0.0

        
        return reading / 65536.0

    @return_type("integer")
    def start_pulserate(self):
        error, = self.rpc(0xab, 0x00, result_format="L")
        return error

    @return_type("integer")
    def stop_pulserate(self):
        error, = self.rpc(0xab, 0x01, result_format="L")
        return error

    @return_type("list(integer)")
    @param('channel', 'integer', desc="Channel to query")
    def get_readings(self, channel):
        count, entry = self.rpc(0xab, 0x03, 0, result_format="LL")

        readings = []
        for i in xrange(0, count):
            count1, reading = self.rpc(0xab, 0x03, channel, i, result_format="LL")

            if count1 <= i:
                break

            readings.append(reading)

        return readings

    @return_type("float")
    @param("channel", 'integer', desc="GPIO pin to sample (2, 4, 5, 6, 7, 8, 9) are possible")
    #@param("power", 'bool', desc="Provide power or not")
    @param("power", 'integer', desc="0-No Power, 1-Power on GPIO0, 10+x-Power on GPIOX")
    @param("delay", 'integer', desc="sampling delay (in ms)")
    def sample_analog(self, channel, power, delay):
        config = 1
        if power == 1:
            config = 2

        elif power >= 10 and power <= 19:
            config = power

        channel_map = {2: 0, 4: 1, 5: 2, 6: 3, 7: 4, 8: 5, 9: 6}

        reading, = self.rpc(0xab, 0x04, channel_map[channel], config, delay, result_format="L")
        return float(reading)/4095 * 2.8

    @return_type("integer")
    @param("channel", 'integer', desc="GPIO pin to control (0-9) are possible")
    @param("enable", 'bool', desc="True to enable, False to disable")
    def enable_digital(self, channel, enable):
        if enable:
            error, = self.rpc(0x80, 0x50+channel, result_format="L")
        else:
            error, = self.rpc(0x80, 0x60+channel, result_format="L")
        return error

    @return_type("integer")
    @param("enable", 'bool', desc="True to enable, False to disable")
    def enable_power(self, enable):
        if enable:
            error, = self.rpc(0x80, 0x5a, result_format="L")
        else:
            error, = self.rpc(0x80, 0x6a, result_format="L")
        return error


    @return_type("integer")
    @param("channel", 'integer', desc="GPIO pin to sample (0-9) are possible")
    def sample_digital(self, channel):
        reading, = self.rpc(0x80, 0x40+channel, result_format="L")
        return reading


    @return_type("float")
    @param("channel", 'integer', desc="GPIO pin to sample (2, 4, 5, 6, 7, 8, 9) are possible")
    def autosample_analog(self, channel):
        channel_map = {2: 0, 4: 1, 5: 2, 6: 3, 7: 4, 8: 5, 9: 6}
        if channel not in channel_map:
            raise ArgumentError("Unsupport analog channel")

        reading, = self.rpc(0x80, 0x30 + channel, result_format="L")
        return float(reading)/4095 * 2.8 

    @return_type("integer")
    def timer_value(self):
        value, = self.rpc(0xab, 0x02, result_format="L")
        return value