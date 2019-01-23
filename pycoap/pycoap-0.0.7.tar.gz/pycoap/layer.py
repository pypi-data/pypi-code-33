

import asyncio
import logging


class BaseLayer(object):
    """ Base Layer object """

    @classmethod
    async def create(cls, destIP, destPort):
        """ 
        Create a Layer instance

        Essentially an async __init__(). 
        Notes: Uses the self var to reinforce that this is an __init__ replacement.
        
        """
        raise NotImplementedError()

        self = cls() #create a new instance
        self.nextLayer = await NextLayer.create(destIP, destPort)
        
        #Since this is not actually an __init__ explicitly return self
        return self
    
    async def start(self):
        await self.nextLayer.start()

    def stop(self):
        self.nextLayer.stop()

    async def send(self,packet):
        await self.nextLayer.send(packet)
    
    async def receive(self):
        return await self.nextLayer.receive()