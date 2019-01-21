"""
homeassistant.components.mixlight
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
MIXLight component that reads input boards.

For more details about this platform, please refer to the documentation at
https://home-assistant.io/components/sensor.mixlight/
"""

import logging
import serial, sys, time, threading, _thread, spidev, traceback
import RPi.GPIO as GPIO


class mixlight_Input(threading.Thread):

  def __init__(self, number, port, link, debug):
    threading.Thread.__init__(self)
    self.number = number
    self.name = port
    
    self.linker = link

    self.port = serial.Serial(port, baudrate=57600, bytesize=8, parity='N', stopbits=1, rtscts=True)
    self.debug = debug

    # prepapre port
    GPIO.setwarnings(False)
    GPIO.setmode(GPIO.BOARD)
    GPIO.setup(12, GPIO.OUT)
    GPIO.output(12, GPIO.LOW)   # HIGH for dmx-out
    # prepare to run
    self.running = False

  def getNumber(self):
    return self.number

  def run(self):
    self.running = True
    logging.info('Starting MIXLIGHT Universe %s on port: %s' % (self.number, self.name))
    self.port.rts = True
    st = time.time()
    i = 0
    cycleIndex = 0
    while self.running:
      try:
        if not self.isAlive() or not self.running: break
        if not self.port.isOpen(): self.port.open()
        notificationList = []
        boardIndex = 0
        boardCache = self.linker.boards
        for addr in boardCache:
          board = self.linker.boards[addr]
          board.execute(self, cycleIndex == boardIndex, self.linker)
          boardIndex = boardIndex + 1
          time.sleep(0.005)
      except Exception as e:
        print("Error in thread mixlight_IN: ", e)        
        traceback.print_exc()
      cycleIndex = (cycleIndex + 1) % (len(self.linker.boards.keys()) + 1)
      i += 1
    logging.info('MIXLiGHT achieved framerate %s: %s' % (self.name, i / (time.time() - st)))
    self.port.rts = False
    self.port.close()
    logging.info('Stopped MIXLIGHT Universe %s on port: %s' % (self.number, self.name))

  def stop(self):
    self.running = False
    self.join()

  def read(self, board_no, read_type, response_len):
    #if board_addr == 1:
    #  return []
    
    self.port.reset_input_buffer()
    self.port.reset_output_buffer()
    GPIO.output(12, GPIO.HIGH)
    bytes = [1, board_no, read_type, 1^ board_no ^ read_type]
    #print('sent ', bytes)
    self.port.write(bytes)
    #time.sleep(0.0005)
    #self.port.flush()
    GPIO.output(12, GPIO.LOW)

    self.port.timeout = 0.003 # * response_len
    result = self.port.read(response_len)

    #print('recv ', result)
    if len(result) < response_len:
      #logging.debug('len-error: {0} < {1}'.format(str(len(result)), str(response_len)))
      time.sleep(0.002)
      return []

    bcc = 0
    for i in range(len(result)):
      bcc = bcc ^ result[i]
    if (result[0] != 1) or (bcc != 0):
      #logging.debug('bcc-error: {0}'.format(str([str(x) for x in result])))
      time.sleep(0.002)
      return []

    #if board_addr != result[2]:
    #  logging.debug('adr-error: {0} : {1}'.format(str(board_addr)), [str(x) for x in result])
    #  return []
    
    #if (board_no == 50 or board_no == 51) and read_type == 2:
    #  logging.trace(bytes)
    #  logging.trace(result)
    
    return result[1:response_len-1]

