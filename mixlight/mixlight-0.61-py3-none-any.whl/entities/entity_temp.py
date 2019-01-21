

import logging

PLATFORM = 'sensor'

PAYLOAD_CONFIG = '{"name": "%s", "unique_id": "%s.%s", "device_class": "temperature", "unit_of_measurement": "°C", "device": %s  }'
PAYLOAD_STATE = '%s'


class entity_Temp():

  def __init__(self, id, addr, name, type, universe):
    self.id = id
    self.addr = addr
    self.name = name
    self.linker = universe.linker
    self.device_info = self.linker.buildDeviceInfo(id, name, '8bths-v2', universe.name)
    self.topic_config = self.linker.buildTopic(PLATFORM, id, "config")
    self.topic_state = self.linker.buildTopic(PLATFORM, id, "state")

  def create(self):
    if self.linker.client is None:
      return
    payload = PAYLOAD_CONFIG % (self.name, PLATFORM, self.id, self.device_info)
    rc = self.linker.client.publish(self.topic_config, payload, 1, True)
    rc.wait_for_publish()
    self.linker.client.will_set(self.topic_config, None, 1, True)
    print (self.id, ' CREATE: ', payload)
    self.write()

  def delete(self):
    if self.linker.client is None:
      return
    rc = self.linker.client.publish(self.topic_config, None, 1, True)
    rc.wait_for_publish()
    print (self.id, ' DELETE: ')

  def get(self):
    return self.linker.boards[self.addr].temp

  def set(self, *data):
    pass

  def read(self, topic, values):
    pass

  def write(self):
    if self.linker.client is None:
      return
    payload = "0"
    if self.get() > 0:
      payload = str(self.get())
    self.linker.client.publish(self.topic_state, payload, 1, True)
