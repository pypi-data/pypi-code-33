"""
homeassistant.components.mixlight
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
MIXLight board representation.

For more details about this platform, please refer to the documentation at
https://home-assistant.io/components/sensor.mixlight/
"""

import logging
import serial, sys, time, threading, _thread, spidev


BIT_2_POWERS = [1, 2, 4, 8, 16, 32, 64, 128]

CMD_BUTTONS = 0
CMD_CLEAN = 1
CMD_TEMP_HUM = 2
CMD_SENSOR = 3


class mixlight_Board:

  def __init__(self, addr, version=1):
    self.version = version
    self.addr = addr
    self.buttons = [0 for i in range (8)]
    self.temp = 0
    self.humi = 0
    self.sensor = 0

  def execute(self, universe, read_sensors, linker):
    response = universe.read(self.addr, CMD_BUTTONS, 3)
    if self.analyze(CMD_BUTTONS, response, linker, universe.getNumber()):
      self.force_execute(CMD_CLEAN, universe, linker, 3, 1)
    if read_sensors:
      self.force_execute(CMD_TEMP_HUM, universe, linker, 6, 1)
      #self.force_execute(CMD_SENSOR, universe, linker, 6, 1)

  def force_execute(self, cmd, uni, link, bytes, count):
      i = 1
      while not self.analyze(cmd, uni.read(self.addr, cmd, bytes), link, uni.getNumber()):
        time.sleep(0.001)
        if count == -1:
          continue
        i = i + 1
        if i >= count:
          return False 
      return True

  def analyze(self, read_type, bytes, linker, uni):
    if len(bytes) == 0:
      return False  
    
    # aici stim ca am avut o comanda corecta
    time.sleep(0.002) # sleep de 2ms dupa comanda

    result = False
    #print('analyze', bytes)    
    #logging.debug('test {0}'.format(str(self.addr)))
    do_print = 0
    if read_type == CMD_BUTTONS:
      if bytes[0] == 0:
        return False
      else:
        i = 0
        for p in BIT_2_POWERS:
          value = bytes[0] & p 
          if value > 0:
            self.buttons[i] = 255 - self.buttons[i]
            linker.change(uni, self.addr, str(i))
            result = True
          i = i + 1
        do_print = 1

    elif read_type == CMD_CLEAN:
      return len(bytes) > 0    

    elif read_type == CMD_TEMP_HUM:
      temp = round((((bytes[2] << 8) | bytes[3]) / 16382) * 165 - 40, 1)
      if self.temp != temp:
        self.temp = temp
        linker.change(uni, self.addr, 'T')
        do_print = 1
      humi = round((((bytes[0] << 8) | bytes[1]) / 16382) * 100, 0)
      if self.humi != humi:
        self.humi = humi
        linker.change(uni, self.addr, 'H')
        do_print = 1

    elif read_type == CMD_SENSOR:
      sensor = (bytes[2] << 8) | bytes[3]
      if self.sensor != sensor:
        self.sensor = sensor
        linker.change(uni, self.addr, 'S')
        do_print = 1
   
    #if do_print == 1:
    #  logging.debug([str(x) for x in self.buttons])
    #  logging.debug([str(x) for x in bytes])
    #logging.debug()

    return result
