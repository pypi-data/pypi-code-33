

from zeroconf import ServiceBrowser, Zeroconf
from socket import inet_ntoa
import time

from .exceptions import DeviceNotFound

import logging


def findDevice(name, timeout=5):
    """ Uses discovery to find the device info for a device name """
    info = None

    def found(found_info):
        nonlocal info
        if found_info["name"] == name:
            info = found_info   

    disco = MTDiscovery(found)

    for x in range(timeout * 10):
        if info is not None:
            return info
        time.sleep(.1)
    
    raise DeviceNotFound("Device {} not found".format(name))

    



class MTDiscovery(object):
    def __init__(self, foundCallback,lostCallback=None):

        self.logger = logging.getLogger(__name__)

        self.SERVICE = "_mtnode-coap._udp.local."
        self.foundCallback = foundCallback
        self.lostCallback = lostCallback

        assert callable(self.foundCallback)
        if self.lostCallback is not None:
            assert callable(self.lostCallback)
        

        self.logger.info("Starting discovery for service {}".format(self.SERVICE))
        self.zeroconf = Zeroconf()
        self.browser = ServiceBrowser(self.zeroconf, self.SERVICE, self)

        self.infoCache = {}


    def normalizeInfo(self, info):
        '''
        normalizes the info data returned by zero conf

        example source info:
        ServiceInfo(type='_mtnode-coap._udp.local.', 
                    name='Garage Master._mtnode-coap._udp.local.', 
                    address=b'\xc0\xa8\x01J', 
                    port=51, 
                    weight=0, 
                    priority=0, 
                    server='garage-master.local.', 
                    properties={b'model': b'LT01', b'firmware': b'0.09.1', b'serial': b'PROTO00003'})
        '''
        normalizedInfo = {}
        normalizedInfo["type"] = info.type
        normalizedInfo["name"] = info.name.split(".")[0] #Extracts the device name from full fqdn
        normalizedInfo["address"] = inet_ntoa(info.address)
        normalizedInfo["port"] = info.port
        normalizedInfo["weight"] = info.weight
        normalizedInfo["priority"] = info.priority
        normalizedInfo["server"] = info.server

        #Add each proptery converting bytes types to strings
        for key,val in info.properties.items():
            normalizedInfo[key.decode(encoding="utf-8")] = val.decode(encoding="utf-8")

        return normalizedInfo



    def add_service(self, zeroconf, service, name, **kwargs):
        '''
        called when the zeroconf browser finds a new device
        method gets called from zeroconf thread which swallows any exceptions
        try/catch block properly logs them:
        '''
        try:        
            info = self.normalizeInfo(self._getServiceInfo(service, name) )
            self.logger.debug("Found '{}' at '{}:{}'".format(info["name"],info["address"],info["port"]  ) )
            self.foundCallback(info)

        except Exception as e:
            self.logger.exception("Exception in Discovery thread")

    def remove_service(self, zeroconf, service, name, **kwargs):
        '''
        called when the zeroconf removes a device from it's cache
        '''
        try:        
            info = self.normalizeInfo(self._getServiceInfo(service, name) )
            self.logger.debug("Lost '{}' at '{}:{}'".format(info["name"],info["address"],info["port"]  ) )
            if self.lostCallback is not None:
                self.lostCallback(info)

        except Exception as e:
            self.logger.exception("Exception in Discovery thread")
    
    def _getServiceInfo(self, service, name):
        """
        Get the service info

        Typically caling zeroconf.get_service_info() returns a ServiceInfo object,
        However, sometimes when a device is removed this info is flushed from the Zeroconf 
        cache before remove_service is called, and zeroconf.get_service_info() will return
        None.  To work around this we cache successfull calls here and return info from 
        this cache if zeroconf.get_service_info() returns None
        """

        info = self.zeroconf.get_service_info(service,name)

        key = (service,name)
        if info is not None:
            self.infoCache[key] = info
            return info
        else:
            return self.infoCache[key]


    def stop(self):
        self.logger.debug("Stoping Zeroconf")
        self.browser.cancel()
        self.zeroconf.close()        



