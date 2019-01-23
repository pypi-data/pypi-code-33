
import asyncio
import logging

import pycoap.constants as C
from pycoap.exceptions import Block1Error, TokenMismatchError
from pycoap.layer import BaseLayer
from pycoap.xmitter import Xmitter as NextLayer


class Block1PacketOrderError(Block1Error):
    pass

class Block1NotSupportedError(Block1Error):
    pass

class Block1UnexpectedResponceError(Block1Error):
    pass

class Block1(BaseLayer):

    #TODO: Add class method to set default block1Size
    @classmethod
    async def create(cls, destIP, destPort):
        """ 
        Create a Layer instance

        Essentially an async __init__(). 
        Notes: Uses the self var to reinforce that this is an __init__ replacement.
        """
        self = cls() #create a new instance
        self.nextLayer = await NextLayer.create(destIP, destPort)
       
        self.block_1_size = 1024
        self.block_1_blocks = []            
        self.block_1_last_num_sent = 0
        self.block_1_sending = False
        self.packet = None
                
        self.logger = logging.getLogger("{}.{}".format(__name__,self.__class__.__name__))

        #Since this is not actually an __init__ explicitly return self
        return self
    
    async def send(self, packet):
        if len(packet.payload) > self.block_1_size:
            self.block_1_sending = True
            self.packet = packet
            self.block_1_blocks = [packet.payload[i:i+self.block_1_size] for i in range(0, len(packet.payload), self.block_1_size)]

            packet.setPayload( self.block_1_blocks[0] )
            packet.setBlock1( 0,True,self.block_1_size )
            self.logger.debug("Sending Block1 Number {} of {}".format(1, len(self.block_1_blocks)))

        await self.nextLayer.send(packet)


    async def receive(self):
        while True:
            resPacket = await self.nextLayer.receive()

            #Move  along, nothing  to see here
            if not self.block_1_sending:
                return resPacket

            elif self.block_1_sending:
                if resPacket.hasBlock1:
                    #Server is asking for the next block1 packet
                    if resPacket.code == C.CODE_CONTINUE and resPacket.block1More:
                        
                        #make sure received token matches sending token
                        if resPacket.token != self.packet.token:
                            raise TokenMismatchError("Received block1 packet has unrecognized token")

                        #Make sure we agree on the last block number sent
                        if resPacket.block1Num != self.block_1_last_num_sent:
                            raise Block1PacketOrderError("Block1 packets arrived out of order")

                        self.logger.debug("Server received block {}".format(self.block_1_last_num_sent +1 ))
                        #send next block
                        self.block_1_last_num_sent += 1
                        this_block_num = self.block_1_last_num_sent
                        more_blocks = this_block_num +1 < len(self.block_1_blocks)
                        blockPacket = self.packet.new()
                        blockPacket.setPayload(self.block_1_blocks[this_block_num])
                        blockPacket.setBlock1( this_block_num,more_blocks,self.block_1_size )
                        self.logger.debug("Sending Block1 Number {} of {}".format(this_block_num+1, len(self.block_1_blocks)))
                        await self.nextLayer.send(blockPacket)

                    #Server received all the  packet
                    elif resPacket.code.isSuccess() and not resPacket.block1More:
                        return resPacket                        

                    #Server responded with a error pass it up the stack
                    elif resPacket.code.isError():
                        return resPacket                        

                    #Somethin unexpected happenned
                    else:
                        raise Block1UnexpectedResponceError("Invalid block1 exchange, receive code {} and block {} ".format(str(resPacket.code), str(resPacket.block1)))

                elif not resPacket.hasBlock1: 
                    raise Block1NotSupportedError("Started block1 but server response is missing block1 option.  Server probably does not support block1")



