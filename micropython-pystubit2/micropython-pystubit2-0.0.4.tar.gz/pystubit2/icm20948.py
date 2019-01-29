"""
------------------------------------------------------------------------------
The MIT License (MIT)
Copyright (c) 2016 Newcastle University
Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:
The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.
THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.import time
------------------------------------------------------------------------------
Author
Kenji Kawase, Artec Co., Ltd. 
We used the script below as reference
https://github.com/loboris/MicroPython_ESP32_psRAM_LoBo/blob/master/MicroPython_BUILD/components/micropython/esp32/modules_examples/drivers/mpu9250.py
------------------------------------------------------------------------------
"""
"""
MicroPython I2C driver for ICM20948 9-axis motion tracking device
"""

from micropython import const
from ak09916 import AK09916
from icm_register_rw import ICMRegisterRW

__version__ = "0.2.0"

_WHO_AM_I = const(0x00)
_GYRO_CONFIG = const(0x01)
_ACCEL_CONFIG = const(0x20)
_ACCEL_CONFIG2 = const(0x21)
_INT_PIN_CFG = const(0x0f)
_ACCEL_XOUT_H = const(0x2d)
_ACCEL_XOUT_L = const(0x2e)
_ACCEL_YOUT_H = const(0x2f)
_ACCEL_YOUT_L = const(0x30)
_ACCEL_ZOUT_H = const(0x31)
_ACCEL_ZOUT_L= const(0x32)
_TEMP_OUT_H = const(0x39)
_TEMP_OUT_L = const(0x3a)
_GYRO_XOUT_H = const(0x33)
_GYRO_XOUT_L = const(0x34)
_GYRO_YOUT_H = const(0x35)
_GYRO_YOUT_L = const(0x36)
_GYRO_ZOUT_H = const(0x37)
_GYRO_ZOUT_L = const(0x38)

#_ACCEL_FS_MASK = const(0b00011000)
ACCEL_FS_SEL_2G =  const(0b00000000)
ACCEL_FS_SEL_4G =  const(0b00000010)
ACCEL_FS_SEL_8G =  const(0b00000100)
ACCEL_FS_SEL_16G = const(0b00000110)

_ACCEL_SO_2G = 16384 # 1 / 16384 ie. 0.061 mg / digit
_ACCEL_SO_4G = 8192 # 1 / 8192 ie. 0.122 mg / digit
_ACCEL_SO_8G = 4096 # 1 / 4096 ie. 0.244 mg / digit
_ACCEL_SO_16G = 2048 # 1 / 2048 ie. 0.488 mg / digit

#_GYRO_FS_MASK = const(0b00011000)
GYRO_FS_SEL_250DPS = const(0b00000000)
GYRO_FS_SEL_500DPS = const(0b00001000)
GYRO_FS_SEL_1000DPS = const(0b00010000)
GYRO_FS_SEL_2000DPS = const(0b00011000)

_GYRO_SO_250DPS = 131
_GYRO_SO_500DPS = 62.5
_GYRO_SO_1000DPS = 32.8
_GYRO_SO_2000DPS = 16.4

# Used for enablind and disabling the i2c bypass access
_I2C_BYPASS_MASK = const(0b00000010)
_I2C_BYPASS_EN = const(0b00000010)
_I2C_BYPASS_DIS = const(0b00000000)

SF_MG = 1000  # mG
SF_M_S2 = 9.80665 # 1 g = 9.80665 m/s2 ie. standard gravity
SF_DEG_S = 1 # deg / s
SF_RAD_S = 57.295779578552 # 1 rad/s is 57.295779578552 deg/s


class ICM20948(ICMRegisterRW):
    ADDR = 0x69
    """Class which provides interface to MPU9250 9-axis motion tracking device."""
    def __init__(self, i2c):
        super().__init__(i2c, ICM20948.ADDR)

        # for AK8963
        buf3 = bytearray('\x00\x00\x00')
        buf1 = bytearray('\x00')
        self._i2c.readfrom_mem_into(ICM20948.ADDR, 0x00, buf1)
        if buf1[0] != 0xea:
            raise RuntimeError("ICM20948 not found in I2C bus.")
        self._i2c.writeto_mem(ICM20948.ADDR, 0x06, b'\x01')  # wake
        self._i2c.writeto_mem(ICM20948.ADDR, 0x0f, b'\x02')  # passthrough
        self._i2c.writeto_mem(ICM20948.ADDR, 0x03, b'\x00')
        self._i2c.scan()  # should now show 12

        self._i2c.writeto_mem(12, 0x31, b'\x1f')  # ROM access
        self._i2c.readfrom_mem_into(12, 0x60, buf3)
    
        self._ak09916 = AK09916(i2c)

        self._accel_so = self._accel_fs(ACCEL_FS_SEL_2G)
        self._gyro_so = self._gyro_fs(GYRO_FS_SEL_250DPS)
        self._accel_sf = SF_M_S2
        self._gyro_sf = SF_DEG_S

        # Enable I2C bypass to access for MPU9250 magnetometer access.
        char = self.register_char(_INT_PIN_CFG)
        char &= ~_I2C_BYPASS_MASK # clear I2C bits
        char |= _I2C_BYPASS_EN
        
        self.register_char(_INT_PIN_CFG, char)

    @property
    def acceleration(self):
        """
        Acceleration measured by the sensor. By default will return a
        3-tuple of X, Y, Z axis acceleration values in mG as integer.
        """
        so = self._accel_so
        sf = self._accel_sf

        xyz = self.register_three_shorts(_ACCEL_XOUT_H)
        return tuple([value / so * sf for value in xyz])

    @property
    def gyro(self):
        """
        X, Y, Z radians per second as floats.
        """
        so = self._gyro_so
        sf = self._gyro_sf

        xyz = self.register_three_shorts(_GYRO_XOUT_H)
        return tuple([value / so * sf for value in xyz])

    @property
    def magnetic(self):
        """
        X, Y, Z axis micro-Tesla (uT) as floats.
        """
        return self._ak09916.magnetic

    @property
    def whoami(self):
        """ Value of the whoami register. """
        return self.register_char(_WHO_AM_I)

    def _accel_fs(self, value):
        self.register_char(_ACCEL_CONFIG, value)

        # Return the sensitivity divider
        if ACCEL_FS_SEL_2G == value:
            return _ACCEL_SO_2G
        elif ACCEL_FS_SEL_4G == value:
            return _ACCEL_SO_4G
        elif ACCEL_FS_SEL_8G == value:
            return _ACCEL_SO_8G
        elif ACCEL_FS_SEL_16G == value:
            return _ACCEL_SO_16G

    def _accel_sf(self, value):
      self._accel_sf = value

    def _gyro_fs(self, value):
        self.register_char(_GYRO_CONFIG, value)

        # Return the sensitivity divider
        if GYRO_FS_SEL_250DPS == value:
            return _GYRO_SO_250DPS
        elif GYRO_FS_SEL_500DPS == value:
            return _GYRO_SO_500DPS
        elif GYRO_FS_SEL_1000DPS == value:
            return _GYRO_SO_1000DPS
        elif GYRO_FS_SEL_2000DPS == value:
            return _GYRO_SO_2000DPS

    def __enter__(self):
        return self

    def __exit__(self, exception_type, exception_value, traceback):
        pass






