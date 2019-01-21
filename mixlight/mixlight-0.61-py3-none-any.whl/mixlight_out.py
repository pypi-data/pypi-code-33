"""
MIXLight component that commands DMX512 stream.

For more details about this platform, please refer to the documentation at
https://home-assistant.io/components/sensor.mixlight/
"""

import logging
import sys, time, threading, _thread, traceback
import spidev
from multiprocessing import Queue


class mixlight_Output(threading.Thread):

  def __init__(self, number, port, link, debug):
    threading.Thread.__init__(self)
    self.number = number
    self.name = port
    self.debug = debug  

    self.linker = link

    self.spi = spidev.SpiDev()
    self.spi.open(0, 0)
    self.spi.mode = 1
    self.spi.bits_per_word = 8
    self.spi.max_speed_hz = 100000
    self.spi.cshigh = False
    self.queue = Queue()

    # prepare to run
    self.data = [0 for i in range(513)] # first is the start code
    self.running = False

  def run(self):
    self.running = True
    logging.info('Starting MIXLIGHT Universe %s on port: %s' % (self.number, self.name))
    st = time.time()
    #self.cleanup()
    i = 0
    while self.running:
      try:
        if not self.isAlive() or not self.running: break
        if self.queue.empty():
          time.sleep(0.005)
        else:
          bytes = self.queue.get()
          self.spi.xfer2(bytes)
      except Exception as e:
        print("Error in threas mixlight_IN: ", e) 
        traceback.print_exc()
      i += 1
    logging.info('MIXLiGHT achieved framerate %s: %s' % (self.name, i / (time.time() - st)))
    self.data = [0 for i in range(513)]
    logging.info('Stopped MIXLIGHT Universe %s on port: %s' % (self.number, self.name))

  def stop(self):
    self.running = False
    self.join()

  def set(self, channel, *data):
    assert channel > 0, 'MIXLIGHT channels start at 1'
    ch = channel
    for val in data:
      assert ch < 512, 'tried to set channel > 512'
      # Ensure value is within allowed range:
      if val < 0: val = 0
      if val > 255: val = 255
      self.data[ch] = val
      bytes = [ (channel-1) & 0xFF, ((channel-1) >> 8) & 0xFF] + [ 0x0D ] + self.data[channel:channel+13]
      self.queue.put(bytes)
      #self.spi.xfer2(bytes)
      ch += 1
      #logging.trace(bytes)
      #logging.trace(self.spi.xfer2(bytes))

  def get(self, channel, count=1):
    assert channel > 0, 'MIXLIGHT channels start at 1'
    assert channel < 512, 'tried to set channel > 512'
    # Ensure value is within allowed range:
    if count == 1: 
      return self.data[channel]
    return self.data[channel: channel+count]

  def cleanup(self):
    channel = 1
    while channel < 512 - 13:
      self.set(channel, 0)
      channel += 13

