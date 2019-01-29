"""
------------------------------------------------------------------------------
The MIT License (MIT)
Copyright (c) 2016 Newcastle University
Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:
The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.
THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.import time
------------------------------------------------------------------------------
Author
Kenji Kawase, Artec Co., Ltd. 
------------------------------------------------------------------------------
"""
import machine, network, io, json, time

class StuduinoBitBLE:
  def __init__(self):
    raise NotImplementedError
    

class StuduinoBitWiFiMixIn:
  def active(self, *args):
    return self._wlan.active(*args)
    
  def isconnected(self, *args):
    return self._wlan.isconnected(*args)
    
  def wifiactive(self):
    return self._wlan.wifiactive()
    
  def ifconfig(self,*args):
    return self._wlan.ifconfig(*args)
    
  def config(self,*args,**kwargs):
    return self._wlan.config(*args,**kwargs)

class StuduinoBitWiFiAP(StuduinoBitWiFiMixIn):
  def __init__(self):
    self._wlan = network.WLAN(network.AP_IF)
    
  def status(self, *args):
    self._wlan.status(*args)

class StuduinoBitWiFiSTA(StuduinoBitWiFiMixIn):
  def __init__(self):
    self._wlan = network.WLAN(network.STA_IF)
    
  def connect(self, *args):
    self._wlan.connect(*args)
    tmo = 50
    while not self._wlan.isconnected():
      time.sleep_ms(100)
      tmo -= 1
      if tmo == 0:
        return False
    return True
    
  def disconnect(self):
    self._wlan.disconnect()
    
  def scan(self):
    return self._wlan.scan()

def CreateWLAN(mode='STA'):
  if mode == 'STA':
    return StuduinoBitWiFiSTA()
  elif mode == 'AP':
    return StuduinoBitWiFiAP()
  else:
    raise TypeError('can\'t start WiFi {0} mode'.format(mode))
    
"""
AUTH_OPEN = network.AUTH_OPEN
AUTH_WEP = network.AUTH_WEP
AUTH_WPA_PSK = network.AUTH_WPA_PSK
AUTH_WPA2_PSK = network.AUTH_WPA2_PSK
AUTH_WPA_WPA2_PSK = network.AUTH_WPA_WPA2_PSK
"""

