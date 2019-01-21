

import logging

class entity_Link():

  def __init__(self, id, addr, nr, name, type, universe):
    self.id = id
    self.addr = addr
    self.number = nr
    self.name = name
    self.linker = universe.linker
    
  def create(self):
    pass

  def delete(self):
    pass

  def get(self):
    pass
    
  def set(self, *data):
    pass

  def read(self, topic, values):
    pass

  def write(self):
    print(self.id, ' toggled ', self.name)
    if self.name in self.linker.entities:
      self.linker.entities[self.name].toggle()
        