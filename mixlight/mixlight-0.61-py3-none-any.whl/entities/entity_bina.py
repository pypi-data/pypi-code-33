

import logging

PLATFORM = 'binary_sensor'

PAYLOAD_CONFIG = '{"name": "%s", "unique_id": "%s.%s", "device_class": "motion", "device": %s }'
PAYLOAD_STATE = '%s'


class entity_Bina():

  def __init__(self, id, addr, nr, name, type, universe):
    self.id = id
    self.addr = addr
    self.number = nr
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
    return self.linker.boards[self.addr].buttons[self.number]  
    
  def set(self, *data):
    pass

  def read(self, topic, values):
    pass

  def write(self):
    if self.linker.client is None:
      return
    payload = "OFF"
    if self.get() > 0:
      payload = "ON"
    self.linker.client.publish(self.topic_state, payload, 1, True)
        
        
