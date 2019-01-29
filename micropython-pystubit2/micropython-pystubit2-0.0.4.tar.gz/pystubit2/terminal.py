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
------------------------------------------------------------------------------
"""
import machine

""" ---------------------------------------------------------------------- """    
""" Pins ----------------------------------------------------------------- """
class StuduinoBitDigitalPinMixin:
  def write_digital(self, value):
    """Write a value to the pin that must be either 0, 1, True  or False.
    """
    if self.pwm != None:
      self.pwm.deinit()
      self.pwm = None
    p = machine.Pin(self.pin, machine.Pin.OUT)
    p.value(value)
  def read_digital(self):
    """Return the pin's value, which will be either 1 or 0.
    """
    if self.pwm != None:
      self.pwm.deinit()
      self.pwm = None
    p = machine.Pin(self.pin, machine.Pin.IN)
    return p.value()
  def write_analog(self, value):
    """Write a value to the pin that must be between 0 and 1023.
    """
    if self.pwm == None:
      self.duty = value
    else:
      self.pwm.duty(value)
  def set_analog_period(self, period, timer=-1):
    """Set the period of the PWM output of the pin in milliseconds.
    
    See https://en.wikipedia.org/wiki/Pulse-width_modulation.
    This is a null operation for the emulation.
    """       
    freq = int(((1.0/period)*1000))
    self.set_analog_hz(freq, timer=timer)
  def set_analog_period_microseconds(self, period, timer=-1):
    """Set the period of the PWM output of the pin in microseconds.
    
    See https://en.wikipedia.org/wiki/Pulse-width_modulation)
    This is a null operation for the emulation.
    """
    freq = int(((1.0/period)*1000*1000))
    self.set_analog_hz(freq, timer=timer)
  def set_analog_hz(self, hz, timer=-1):
    # print("pin:{0}, hz:{1}, duty:{2}, timer:{3}".format(self.pin, hz, self.duty, timer))
    if self.pwm == None:
      machine.Pin(self.pin, machine.Pin.OUT)
      self.pwm = machine.PWM(self.pin, hz, self.duty, timer=timer)
    else:
      self.pwm.freq(hz)
  def status(self):
    machine.PWM.list()
  
class StuduinoBitAnalogPinMixin():
  """Returns the pin's value, which will be between 0 and 1023
  """
  def read_analog(self, mv=False):
    if self.adc == None:
      self.adc = machine.ADC(self.pin)
      self.adc.atten(self.adc.ATTN_11DB)
    
    if mv:
      return self.adc.read()
    else:
      raw = self.adc.readraw()
      calib = self.adc.read()
      if (raw >= 150) and (raw <= 2450):
        val = calib / 3300 * 4095
      else:
        val = raw
      return val
        

class StuduinoBitDigitalPin(StuduinoBitDigitalPinMixin):
  def __init__(self, pin):
    self.pin = pin
    self.duty = 0
    self.pwm = None

class StuduinoBitAnalogPin(StuduinoBitAnalogPinMixin):
  def __init__(self, pin):
    self.pin = pin
    self.adc = None

class StuduinoBitAnalogDitialPin(StuduinoBitDigitalPinMixin, StuduinoBitAnalogPinMixin):
  def __init__(self, pin):
    self.pin = pin
    self.duty = 0
    self.pwm = None
    self.adc = None
    
  def write_digital(self, value):
    if self.adc != None:
      self.adc.deinit()
      self.adc = None
    super().write_digital(value)
  def read_digital(self):
    if self.adc != None:
      self.adc.deinit()
      self.adc = None
    return super().read_digital()
  def write_analog(self, value):
    if self.adc != None:
      self.adc.deinit()
      self.adc = None
    super().write_analog(value)
  def set_analog_hz(self, hz, timer=-1):
    if self.adc != None:
      self.adc.deinit()
      self.adc = None
    super().set_analog_hz(hz, timer)
  def read_analog(self, mv=False):
    if self.pwm != None:
      self.pwm.deinit()
      self.pwm = None
    return super().read_analog(mv)
      

p0  = StuduinoBitAnalogDitialPin(32)
p1  = StuduinoBitAnalogDitialPin(33)
p2  = StuduinoBitAnalogPin(36)
p3  = StuduinoBitAnalogPin(39)
p4  = StuduinoBitDigitalPin(25)
p5  = StuduinoBitAnalogDitialPin(15)
p6  = StuduinoBitDigitalPin(26)
p7  = StuduinoBitDigitalPin(5)
p8  = StuduinoBitAnalogDitialPin(14)
p9  = StuduinoBitAnalogDitialPin(12)
p10 = StuduinoBitDigitalPin(0)
p11 = StuduinoBitDigitalPin(27)
p12 = StuduinoBitDigitalPin(4)
p13 = StuduinoBitDigitalPin(18)
p14 = StuduinoBitDigitalPin(19)
p15 = StuduinoBitDigitalPin(23)
p16 = StuduinoBitAnalogDitialPin(13)
p19 = StuduinoBitDigitalPin(22)
p20 = StuduinoBitDigitalPin(21)




if __name__ == '__main__':
  pass













