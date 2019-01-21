

import logging
import colorsys

PLATFORM = 'light'

PAYLOAD_CONFIG = '{"name": "%s", "unique_id": "%s.%s", "command_topic": "%s", "schema": "json", "hs": "true", "brightness":"true", "device": %s  }'
PAYLOAD_STATE = '{ "brightness": %s, "state": "%s", "color": { "h": %s, "s": %s } }'


class entity_RGB():

  def __init__(self, id, addr, name, type, universe):
    self.id = id
    self.addr = addr
    self.name = name
    self.linker = universe.linker
    self.device_info = self.linker.buildDeviceInfo(id, name, 'dmx512', universe.name)
    self.hsb = [270, 0, 255]
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
    rgb = self.linker.output.get(self.addr, 3)
    return self.color_rgb_to_hsb(rgb[1], rgb[0], rgb[2])
    
  def set(self, *data):
    rgb = self.color_hsb_to_rgb(data[0], data[1], data[2])
    self.linker.output.set(self.addr, rgb[1], rgb[0], rgb[2])
    self.write()
    
  def read(self, topic, values):
    #print('READ ', topic, ' ', values)
    if topic == self.topic_set:    
      if 'color' in values:
        hs = values['color']
        if 'h' in hs:
          self.hsb[0] = hs['h']
        if 's' in hs:
          self.hsb[1] = hs['s']
      if 'brightness' in values:
        self.hsb[2] = values['brightness']
      if 'state' in values:
        if values['state'] == "ON":
          self.set(self.hsb[0], self.hsb[1], self.hsb[2])
        elif values['state'] == "OFF":
          self.set(0, 0, 0)

  def write(self):
    if self.linker.client is None:
      return
    payload = "OFF"
    hsb = self.get()
    if hsb[2] > 0:
      payload = "ON"
    payload = PAYLOAD_STATE % (int(hsb[2]), payload, hsb[0], hsb[1])  
    #print ('WRITE: ', payload)
    self.linker.client.publish(self.topic_state, payload, 1, True)

  def toggle(self):
    rgb = self.get()
    if rgb[2] > 0:
      self.set(0, 0, 0)
    else:
      self.set(self.hsb[0], self.hsb[1], self.hsb[2])      

  def color_hsb_to_rgb(self, fH, fS, iB):
    """Convert an hsv color into its rgb representation.
    Hue is scaled 0-360
    Sat is scaled 0-100
    Val is scaled 0-255
    """
    fRGB = colorsys.hsv_to_rgb(fH/360, fS/100, iB/255)
    return [int(fRGB[0]*255), int(fRGB[1]*255), int(fRGB[2]*255)]

  def color_rgb_to_hsb(self, iR, iG, iB):
    """Convert an rgb color to its hsv representation.
    Hue is scaled 0-360
    Sat is scaled 0-100
    Val is scaled 0-255
    """
    fHSV = colorsys.rgb_to_hsv(iR/255.0, iG/255.0, iB/255.0)
    return [round(fHSV[0]*360, 3), round(fHSV[1]*100, 3), round(fHSV[2]*255, 3)]
  