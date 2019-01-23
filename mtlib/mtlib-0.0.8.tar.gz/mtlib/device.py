
import asyncio
import inspect
import json
import logging
import socket
from threading import Thread

import pycoap
from pycoap.client import Client

from .exceptions import *

#from .exception import MTException



class Device(object):
    def __init__(self,host, port=5683):
        self.host = host
        self.port = port
        self._observation = None
        self._protocol = None

        self._coap = Client()

        self.logger = logging.getLogger(__name__)


    ########################################################################################
    #
    # Async Methods
    #
    ########################################################################################
    

    async def async_get_state(self):
        """Gets current state of device asynchronously
        
        Returns:
            string: The state (i.e. "ON", "OFF", "OPEN" or "CLOSED")

        Raises:
            mtlib.exceptions.MTException
        """
        uri = "coap://{}:{}/state.json".format(self.host,self.port)
        self.logger.debug("Getting state at {}".format( uri ) )

        result = await self._coap.get(uri)

        #Config the  request was successfull
        if result.code != "2.05":
            raise ResponseError("COAP response Code: {}, Payoad:{}".format(result.code,result.payload))

        #Parse the json data
        try:
            data = json.loads(result.payload.decode("utf-8"))
        except json.decoder.JSONDecodeError:
            raise ResponseError("Invalid state data.  JSON Error decoding: {}".format(result.payload))

        #Make sure state is in the data
        if not result.code.isSuccess():
            raise ResponseError("Invalid response - Does not contain 'state' key: {}".format(data))

        state = data["state"] 

        self.logger.debug("State at {} is {}".format( uri, state ) )
        return state

    async def async_get_log(self):
        """Gets current debug log asynchronously
        
        Returns:
            string: The debug log contents

        Raises:
            mtlib.exceptions.MTException
        """
        uri = "coap://{}:{}/debug.log".format(self.host,self.port)
        self.logger.debug("Getting log at {}".format( uri ) )

        result = await self._coap.get(uri)

        #Config the  request was successfull
        if not result.code.isSuccess():
            raise ResponseError("COAP response Code: {}, Payoad:{}".format(result.code,result.payload))

        data  = result.payload.decode("utf-8")
        return data


    async def async_get_info(self):
        """Retrieves a dict of info about the device asynchronously
        
        Returns:
            dict: Information about the devide.  Includes deviceName, model, serial.
                Other attributes may be included depending on the device.
        
        Raises: 
            mtlib.exceptions.MTException
        """
        uri = "coap://{}:{}/info.json".format(self.host,self.port)
        self.logger.debug("Getting info at {}".format( uri ) )

        result = await self._coap.get(uri, acceptFormat="application/json")

        #Config the  request was successfull
        if not result.code.isSuccess():
            raise ResponseError("COAP response Code: {}, Payoad:{}".format(result.code,result.payload))

        #Confirm the content format
        content_format = result.options.get("Content-Format")
        if content_format != "application/json":
            raise ResponseError("Invalid content format '{}'.  Should be 'application/json' ".format(content_format) )

        #Parse the json data
        try:
            data = json.loads(result.payload.decode("utf-8"))
        except json.decoder.JSONDecodeError:
            raise ResponseError("Invalid state data.  JSON Error decoding: {}".format(result.payload))

        #All is good, return the info dict
        self.logger.debug("Info at {} is {}".format( uri, data ) )
        return data


    async def async_send_command(self, command):
        """Sends a command to the device asynchronously

        Args:
            command (string): The command to send.  (i.e. "ON", "OFF", "OPEN" or "CLOSE")

        Returns: 
            bool: True on success
        
        Raises:
            mtlib.exceptions.MTException
        """
        uri = "coap://{}:{}/command".format(self.host, self.port)
        self.logger.debug("Sending command '{}' to {}".format( command, uri ) )

        result = await self._coap.post(uri,payload=command)

        #Config the  request was successfull
        if not result.code.isSuccess():
            raise ResponseError("COAP response Code: {}, Payoad:{}".format(result.code,result.payload))

        # result = await self._coap_post(uri,payload=command)

        # #Confirm the  request was successfull
        # if not result.code.is_successful():
        #     raise  ResponseError("COAP response Code: {}, Payoad:{}".format(result.code,result.payload))

        self.logger.debug("Command '{}' to {} succeeded".format( command, uri ) )
        return True

    async def async_on(self):
        """Sends "ON" command to the device asynchronously

        Returns: 
            bool: True on success
        
        Raises:
            mtlib.exceptions.MTException
        """
        return await self.async_send_command("ON")
    

    async def async_off(self):
        """Sends "OFF" command to the device asynchronously

        Returns: 
            bool: True on success
        
        Raises:
            mtlib.exceptions.MTException
        """
        return await self.async_send_command("OFF")


    async def async_toggle(self):
        """Sends "TOGGLE" command to the device asynchronously

        Returns: 
            bool: True on success
        
        Raises:
            mtlib.exceptions.MTException
        """
        return await self.async_send_command("TOGGLE")



    async def async_observe(self, callback=None):

        assert callable(callback) or callback is None

        uri = "coap://{}:{}/state.json".format(self.host,self.port)

        self.logger.debug("Observing state at {}".format( uri ) )

        if self._observation is None:
            self._observation = await self._coap.observe(uri)
        
        await self._observation.register()

        async for result in self._observation.observe():
            #Config the  request was successfull
            if result.code != "2.05":
                raise ResponseError("COAP response Code: {}, Payoad:{}".format(result.code,result.payload))

            #Parse the json data
            try:
                data = json.loads(result.payload.decode("utf-8"))
            except json.decoder.JSONDecodeError:
                raise ResponseError("Invalid state data.  JSON Error decoding: {}".format(result.payload))

            #Make sure state is in the data
            if not result.code.isSuccess():
                raise ResponseError("Invalid response - Does not contain 'state' key: {}".format(data))

            state = data["state"] 

            if callable(callback):
                callback(state)

            yield state


    def stop_observe(self):
        self._observation.stop()






    ########################################################################################
    #
    # Sync Methods
    #
    ########################################################################################


    def get_state(self):
        """
        Retrieves the current state of the device
        Synchronous version of async_get_state()

        @returns: string (i.e. "ON", "OFF", "OPEN" or "CLOSED") 
        @raises: MTException on errors
        """
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        result = loop.run_until_complete( self.async_get_state() )
        
        if isinstance(result,MTException):
            raise result
        else:
            return result

    def get_log(self):
        """
        Retrieves debug log from the device
        Synchronous version of async_get_log()

        @returns: string (i.e. "ON", "OFF", "OPEN" or "CLOSED") 
        @raises: MTException on errors
        """
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        result = loop.run_until_complete( self.async_get_log() )
        
        if isinstance(result,MTException):
            raise result
        else:
            return result

    def get_info(self):
        """
        Retrieves a dict of info about the device.
        Synchronous version of async_get_info()
    
        @returns: dict - include deviceName, model, serial.  Other attributes may be included depending on the device.
        @raises: MTException 
        """
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        result = loop.run_until_complete( self.async_get_info() )
        
        if isinstance(result,MTException):
            raise result
        else:
            return result

    def send_command(self,command):
        """
        Sends a command to the device.
        Synchronous version of async_send_command()

        @param command: string - The command to send.  (i.e. "ON", "OFF", "OPEN" or "CLOSE")
        @returns: True on success
        @raises: MTException 
        """
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        result = loop.run_until_complete( self.async_send_command(command) )
        
        if isinstance(result,MTException):
            raise result
        else:
            return result

    def on(self):
        """
        Sends command "ON" to device
        """
        return self.send_command("ON")

    def off(self):
        """
        Sends command "OFF" to device
        """
        return self.send_command("OFF")

    def toggle(self):
        """
        Sends command TOGGLE to device
        """
        return self.send_command("TOGGLE")


    # def observe(self, callback):
    #     """
    #     Observes the current state of the device
    #     Synchronous version of async_get_state()

    #     @param: callable( state: string ) - Callback function.  When start on device changes the callback
    #            function is called with the new state
                           
    #     """
    #     assert callable(callback)

    #     def start_loop(loop):
    #         asyncio.set_event_loop(loop)
    #         loop.run_forever()

    #     loop = asyncio.new_event_loop()
    #     t = Thread(target=start_loop, args=(loop,))
    #     t.start()

    #     loop.call_soon_threadsafe(asyncio.async, self.async_observe(callback))
