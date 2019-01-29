
import ustruct
from micropython import const

class ICMRegisterRW:
  def __init__(self, i2c, address):
    self._i2c = i2c
    self._address = address
  
  def register_short(self, register, value=None, buf=bytearray(2), endian='b'):
    if endian is 'b':
      fmt = ">h"
    else:
      fmt = "<h"
      
    if value is None:
      self._i2c.readfrom_mem_into(self._address, register, buf)
      return ustruct.unpack(fmt, buf)[0]

    ustruct.pack_into(fmt, buf, 0, value)
    return self._i2c.writeto_mem(self._address, register, buf)

  def register_three_shorts(self, register, buf=bytearray(6), endian='b'):
    if endian is 'b':
      fmt = ">hhh"
    else:
      fmt = "<hhh"

    self._i2c.readfrom_mem_into(self._address, register, buf)
    return ustruct.unpack(fmt, buf)

  def register_char(self, register, value=None, buf=bytearray(1)):
    if value is None:
      self._i2c.readfrom_mem_into(self._address, register, buf)
      return buf[0]

    ustruct.pack_into("<b", buf, 0, value)
    return self._i2c.writeto_mem(self._address, register, buf)  
    
