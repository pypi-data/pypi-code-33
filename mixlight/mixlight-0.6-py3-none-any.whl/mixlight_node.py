"""
homeassistant.components.mixlight
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
MIXLight main service .

For more details about this platform, please refer to the documentation at
https://home-assistant.io/components/sensor.mixlight/
"""

import logging
import os, sys, time, yaml, json, traceback
import paho.mqtt.client as mqtt
from multiprocessing import Queue

from mixlight.mixlight_in import mixlight_Input
from mixlight.mixlight_board import mixlight_Board
from mixlight.entities.entity_bina import entity_Bina
from mixlight.entities.entity_link import entity_Link
from mixlight.entities.entity_temp import entity_Temp
from mixlight.entities.entity_humi import entity_Humi

from mixlight.mixlight_out import mixlight_Output
from mixlight.entities.entity_switch import entity_Switch
from mixlight.entities.entity_light import entity_Light
from mixlight.entities.entity_dimmer import entity_Dimmer
from mixlight.entities.entity_rgb import entity_RGB
from mixlight.entities.entity_flux import entity_Flux


TOPIC_FORMAT = "%s/%s/%s/%s"
MQTT_TRACE_MSG = "MQTT:\n  topic: %s\n  payload= %s\n  qos: %s\n  retain: %s"

SW_VERSION = '1.0'
DOMAIN = 'mqtt'
DEVICE_INFO = '{ "identifiers": "%s", "name": "%s", "manufacturer": "MIXLIGHT Romania", "model": "%s", "sw_version": "%s" } '

class mixlight_Node():

  def __init__(self, config_folder = "."):
    self.folder = config_folder
    self.input = None
    self.output = None
    self.entities = {}
    self.boards = {}
    self.lastLoad = 0
    self.connected = False
    self.broker = "localhost"
    self.port = 1883
    self.keepalive = 60
    self.client_id = "MIXLIGHT"
    self.min_delay = 1
    self.max_delay = 120
    self.prefix = "homeassistant"
    self.client = mqtt.Client("MIXLIGHT", clean_session=True)
    self.queue = Queue()

  def start(self):
    logging.info('Starting MIXLIGHT : %s' % (self.folder))
    self.output.start()
    self.input.start()
    self.connected = False
    logging.info('Starting MQTT client: %s' % (self.folder))
    self.client = mqtt.Client(self.client_id, clean_session=True)
    self.client.on_connect = self.mqtt_on_connect
    self.client.on_message = self.mqtt_on_message
    self.client.on_disconnect = self.mqtt_on_disconnect
    self.client.reconnect_delay_set(self.min_delay, self.max_delay)
    #self.client.connect_async(self.broker, self.port)
    self.client.connect(self.broker, self.port)
    self.client.loop_start()

  def stop(self):
    logging.info('Stopping MIXLIGHT : %s' % (self.folder))
    if not self.input is None:
      self.input.stop()
    if not self.output is None:
      self.output.stop()
    logging.info('Stopping MQTT client : %s' % (self.folder))
    self.client.disconnect()
    self.client.loop_stop()

  def mqtt_on_connect(self, client, userdata, flags, rc):
    if rc == 0:
      self.connected = True
      print('Connect: !!! CONNECTED !!!')
    else:
      self.connected = False
      print('Connect: !!! NOT CONNECTED !!!')

  def mqtt_on_message(self, client, userdata, message):
    try:
      payload = str(message.payload.decode("utf-8"))
      #print ('MSG: ', message.topic, ' ', payload)
      #if True:
      #  logging.info(MQTT_TRACE_MSG % (message.topic, payload, message.qos, message.retain))
      if payload.startswith("{"):
        values = json.loads(payload)
        payload = values
      for entity in self.entities:
        self.entities[entity].read(message.topic, payload)
    except Exception as e:
      print("Error in MQTT on_message: ", e)
      traceback.print_exc()

  def mqtt_on_disconnect(self, client, userdata, rc):
    self.connected = False
    if rc == 0:
      print('Disconnect: !!! NOT CONNECTED !!!')
    else:
      print('Lost: !!! NOT CONNECTED !!!')

  def load_config(self):
    with open(self.folder + "/mixlight.yaml", "r") as ymlfile:
      cfg = yaml.load(ymlfile)
    # read mqtt configuration
    if 'mqtt' in cfg:
      mqtt = cfg['mqtt']
      if 'port' in mqtt:
        self.port = int(mqtt['port'])
      if 'broker' in mqtt:
        self.broker = mqtt['broker']
      if 'client_id' in mqtt:
        self.client_id = mqtt['client_id']
      if 'keepalive' in mqtt:
        self.keepalive = mqtt['keepalive']
      if 'min_delay' in mqtt:
        self.min_delay = mqtt['min_delay']
      if 'max_delay' in mqtt:
        self.max_delay = mqtt['max_delay']
      if 'prefix' in mqtt:
        self.prefix = mqtt['prefix']
    # read input comm configuration
    if 'input' in cfg:
      input = cfg['input']
      if ('port' in input) and ('universe' in input):
        self.input = mixlight_Input(input['universe'], input['port'], self, False)
    # read output comm configuration
    if 'output' in cfg:
      output = cfg['output']
      if ('port' in output) and ('universe' in output):
        self.output = mixlight_Output(output['universe'], output['port'], self, False)

  def check_entities(self):
    filePath = self.folder + "/entities.yaml"
    fileStamp = os.path.getmtime(filePath)
    if fileStamp <= self.lastLoad:
      return
    self.lastLoad = fileStamp
    self.unregister()
    self.load_entities()
    self.register()

  def load_entities(self):
    self.entities = {}
    with open(self.folder + "/entities.yaml", 'r') as ymlfile:
      cfg = yaml.load(ymlfile)
    # read ouput entities
    if 'output' in cfg:
      output = cfg['output']
      universe = output['universe']
      for type in output:
        if type == 'universe':
          continue
        for value in output[type]:
          addr = next(iter(value))
          name = value[addr]
          id = "MIX_O%s_E%s" % (universe, addr)
          if type == 'switch':
            self.entities[id] = entity_Switch(id, addr, name, type, self.output)
          elif type == 'light':
            self.entities[id] = entity_Light(id, addr, name, type, self.output)
          elif type == 'dimmer':
            self.entities[id] = entity_Dimmer(id, addr, name, type, self.output)
          elif type == 'rgb':
            self.entities[id] = entity_RGB(id, addr, name, type, self.output)
          elif type == 'flux':
            self.entities[id] = entity_Flux(id, addr, name, type, self.output)
    # read input entities
    if 'input' in cfg:
      input = cfg['input']
      universe = input['universe']
      for group in input['boards']:
        if not 'address' in group:
          continue
        board = group['address']
        self.boards[board] = mixlight_Board(board)
        for type in group:
          if type == 'address':
            continue
          conf = group[type]
          if type == 'temperature':
            id = "MIX_I%s_B%s_ET" % (universe, board)
            self.entities[id] = entity_Temp(id, board, conf, type, self.input)
          elif type == 'humidity':
            id = "MIX_I%s_B%s_EH" % (universe, board)
            self.entities[id] = entity_Humi(id, board, conf, type, self.input)
          elif type == 'sensor':
            id = "MIX_I%s_B%s_ES" % (universe, board)
            self.entities[id] = entity_Sens(id, board, conf, type, self.input)
          else:
            for value in conf:
              nr = next(iter(value))
              name = value[nr]
              id = "MIX_I%s_B%s_E%s" % (universe, board, nr)
              if name in self.entities:
                self.entities[id] = entity_Link(id, board, nr, name, type, self.input)
              else:
                self.entities[id] = entity_Bina(id, board, nr, name, type, self.input)

  def buildTopic(self, platform, id, action):
    return TOPIC_FORMAT % (self.prefix, platform, id, action)

  def buildDeviceInfo(self, id, name, model, port):
    return DEVICE_INFO % (id, name, model, SW_VERSION)

  def register(self):
    for name in self.entities:
      self.entities[name].create()

  def unregister(self):
    for name in self.entities:
      self.entities[name].delete()

  def change(self, uni, board, nr):
    id = "MIX_I%s_B%s_E%s" % (uni, board, nr)
    #print('CHANGE: ', id)
    self.queue.put(id)

  def write_changes(self):
    while not self.queue.empty():
      entityName = self.queue.get()
      if entityName in self.entities:
        #print('WRITE: ', entityName)
        self.entities[entityName].write()


