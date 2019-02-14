# The MIT License (MIT)

# Copyright (c) 2018, Tangliufeng. LabPlus

# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.

"""
# blue:bit modules library for mPython
#
"""
from mpython import i2c,sleep_ms

class SHT20(object):
# bluebit sht20 modules driver
    def temperature(self):
        ''' Return temperature,unit Celsius'''
        i2c.writeto(0x40,b'\xf3',False)
        sleep_ms(70)
        t=i2c.readfrom(0x40, 2)
        return -46.86+175.72*(t[0]*256+t[1])/65535

    def humidity(self):
        """ Return humidity ,unit %  """
        i2c.writeto(0x40,b'\xf5',False)
        sleep_ms(25)
        t=i2c.readfrom(0x40, 2)
        return -6+125*(t[0]*256+t[1])/65535

