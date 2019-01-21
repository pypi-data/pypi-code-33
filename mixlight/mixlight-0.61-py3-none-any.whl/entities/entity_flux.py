

import logging
import colorsys

PLATFORM = 'light'

PAYLOAD_CONFIG = '{"name": "%s", "unique_id": "%s.%s", "command_topic": "%s", "schema": "json", "color_temp": "true", "brightness":"true", "device": %s  }'
PAYLOAD_STATE = '{ "brightness": %s, "state": "%s", "color_temp": %s }'


class entity_Flux():

  def __init__(self, id, addr, name, type, universe):
    self.id = id
    self.addr = addr
    self.name = name
    self.linker = universe.linker
    self.device_info = self.linker.buildDeviceInfo(id, name, 'dmx512', universe.name)
    self.temp_bri = [153, 255]
    self.topic_config = self.linker.buildTopic(PLATFORM, id, "config")
    self.topic_state = self.linker.buildTopic(PLATFORM, id, "state")
    self.topic_set = self.linker.buildTopic(PLATFORM, id, "set")

  def create(self):
    if self.linker.client is None:
      return
    payload = PAYLOAD_CONFIG % (self.name, PLATFORM, self.id, self.topic_set, self.device_info)
    rc = self.linker.client.publish(self.topic_config, payload, 1, True)
    rc.wait_for_publish()
    self.linker.client.will_set(self.topic_config, None, 1, True)
    self.linker.client.subscribe(self.topic_set)
    print (self.id, ' CREATE: ', payload)
    self.write()

  def delete(self):
    if self.linker.client is None:
      return
    self.linker.client.unsubscribe(self.topic_set)
    rc = self.linker.client.publish(self.topic_config, None, 1, True)
    rc.wait_for_publish()
    print (self.id, ' DELETE: ')

  def get(self):
    return self.temp_bri

  def set(self, *data):
    val = self.tempbri_to_values(data[0], data[1])
    self.linker.output.set(self.addr, val[0], val[1])
    self.write()

  def read(self, topic, values):
    #print('READ ', topic, ' ', values)
    if topic == self.topic_set:
      if 'color_temp' in values:
        self.temp_bri[0] = values['color_temp']
      if 'brightness' in values:
        self.temp_bri[1] = values['brightness']
      if 'state' in values:
        if values['state'] == "ON":
          self.set(self.temp_bri[0], self.temp_bri[1])
        elif values['state'] == "OFF":
          self.set(0, 0)

  def write(self):
    if self.linker.client is None:
      return
    payload = "OFF"
    temp_bri = self.get()
    if temp_bri[1] > 0:
      payload = "ON"
    payload = PAYLOAD_STATE % (temp_bri[1], payload, temp_bri[0])
    print ('WRITE: ', payload)
    self.linker.client.publish(self.topic_state, payload, 1, True)

  def toggle(self):
    tb = self.get()
    if tb[1] > 0:
      self.set(0, 0)
    else:
      self.set(self.temp_bri[0], self.temp_bri[1])

  def tempbri_to_values(self, t, b):
    p1 = round((t - 153) / (500 - 153), 2) * 100
    p2 = round(100 - p1, 2)
    m = max(p1, p2)
    vals = [int(p1 / m * b), int(p2 / m * b)]
    return vals
