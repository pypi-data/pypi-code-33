

import asyncio
import logging

import pycoap.constants as C
from pycoap.exceptions import TokenMismatchError, Block2Error
from pycoap.layer import BaseLayer
from pycoap.block1 import Block1 as NextLayer
from pycoap.buffer import Buffer


class Block2PacketOrderError(Block2Error):
    pass

class Block2NonBlock2AfterEstablish(Block2Error):
    pass

class Block2PayloadSizeError(Block2Error):
    pass

class Block2(BaseLayer):

    @classmethod
    async def create(cls, destIP, destPort):
        """ 
        Create a Layer instance

        Essentially an async __init__(). 
        Notes: Uses the self var to reinforce that this is an __init__ replacement.
        """
        self = cls() #create a new instance
        self.nextLayer = await NextLayer.create(destIP, destPort)
       
        self.req_packet = None
        self.block_buffer = Buffer()
        self.next_block_num = 0
        self.block_2_receiving = False
                
        self.logger = logging.getLogger("{}.{}".format(__name__,self.__class__.__name__))

        #Since this is not actually an __init__ explicitly return self
        return self

    async def send(self,packet):
        #save a copy of the request packet 
        self.req_packet = packet

        await self.nextLayer.send(packet)

    async def receive(self):
        while True:
            resp_packet = await self.nextLayer.receive()

            #Check for a wierd error
            if self.block_2_receiving and not resp_packet.hasBlock2:
                raise Block2NonBlock2AfterEstablish("Server sent a non block2 packet after already extablising a block2 session")

            #Move  along, nothing to see here (just pass the non block2 packet up to the next layer)
            elif not resp_packet.hasBlock2:
                return resp_packet

            elif resp_packet.hasBlock2:

                #make sure received token matches sending token
                if resp_packet.token != self.req_packet.token:
                    raise TokenMismatchError("Received block2 packet has unrecognized token")

                #Check for the correct block num
                if resp_packet.block2Num != self.next_block_num:
                    raise Block2PacketOrderError("Block2 packets arrived out of order")

                #Check that the received payload size matches block size
                #Does not apply to the last block, ie block2More is false
                if resp_packet.block2More and len(resp_packet.payload) != resp_packet.block2Size:
                    raise Block2PayloadSizeError("Payload size does not match block size")

                #append paload to receive buffer
                self.block_buffer.extend(bytes(resp_packet.payload))

                #If there are more packets:
                if resp_packet.block2More: 
                    self.logger.debug("Received Block2 block number {}".format(resp_packet.block2Num))

                    #request next block
                    self.next_block_num += 1

                    block_packet = self.req_packet.new()
                    block_packet.setBlock2( self.next_block_num, True, resp_packet.block2Size )
                    self.logger.debug("Sending Request Packet for Block2 block number:{}".format(self.next_block_num))
                    await self.nextLayer.send(block_packet )
                    continue

                #If this is the last block
                else:
                    #Inject the buffer into the packet and return it
                    self.logger.debug("Received Block2 block number {} as last block".format(resp_packet.block2Num))
                    resp_packet.setPayload(self.block_buffer)
                    return resp_packet




        # self.block1Size = 1024 if block1Size is None else block1Size
        # self.block1Blocks = []            
        # self.block1LastNumSent = 0
        # self.block1Sending = False

        # self.block2Buffer = Payload()
        # self.block2NextBlockNum = 0
        # self.block2Receiving = False





   # async def oldsend(self):
    #     #Check for a large payload that requires sending in blocks
    #     if len(self.payload) > self.block1Size:
    #         self.block1Sending = True
    #         self.block1Blocks = [self.payload[i:i+self.block1Size] for i in range(0, len(self.payload), self.block1Size)]

    #         payloadParam = self.block1Blocks[0]
    #         block1Param = (0,True,self.block1Size)
    #         self.logger.debug("Request {0} - Sending Request Packet - Block1 Number:{1} of {2}".format(self.reqNum, 1, len(self.block1Blocks)))

    #     else:
    #         payloadParam = self.payload
    #         block1Param = None
    #         self.logger.debug("Request {0} - Sending Request Packet".format(self.reqNum) )


    #     reqPacket = Packet(messageType=self.messageType, code=self.code, messageID=self.nextMessageID(), token=self.token,
    #                         hostname=self.hostname, port=self.port, pathSegments=self.pathSegments, queryParams=self.queryParams,
    #                         payload=payloadParam, contentFormat=self.contentFormat, acceptFormat=self.acceptFormat, 
    #                         block1=block1Param )

    #     self.packetTransmitter.send(reqPacket)
    #     await self.done.wait()
        
    #     if isinstance(self.response, Exception): 
    #         raise self.response
    #     else:
    #         return self.response









    # def onResponse(self, resPacket):
    #     self.logger.debug("Request {0} - Received Response Packet".format(self.reqNum) )

    #     if self.compleated:
    #         #Ignore the packet if Message is already compleated
    #         self.logger.warning("Request {0} - Packate received for compleated request, probably a duplicate".format(self.reqNum))
    #         return

    #     #If packet code is in the response range
    #     if resPacket.isResponse:

    #         #Make sure the token matches
    #         if resPacket.token != self.token:
    #             #Ignore packet if Message ID does not match
    #             self.logger.error("Request {0} - Ignoring packet with token mismatch".format(self.reqNum))
    #             return

    #         #handle Block1 responses
    #         if self.block1Sending and resPacket.code == C.CODE_CONTINUE:
    #             #Make sure we agree on the last block number sent
    #             if resPacket.block1Num != self.block1LastNumSent:
    #                 self.onError(ProtocolError("Block1 packets arrived out of order"))
    #                 return

    #             #send next block
    #             self.block1LastNumSent += 1
    #             thisBlockNum = self.block1LastNumSent
    #             moreBlocks = thisBlockNum +1 < len(self.block1Blocks)
    #             blockPacket = Packet(messageType=self.messageType, code=self.code, messageID=self.nextMessageID(), token=self.token,
    #                                 hostname=self.hostname, port=self.port, pathSegments=self.pathSegments, queryParams=self.queryParams, 
    #                                 payload=self.block1Blocks[thisBlockNum], contentFormat=self.contentFormat,
    #                                 acceptFormat=self.acceptFormat, block1=(thisBlockNum,moreBlocks,self.block1Size)  )
    #             self.logger.debug("Request {0} - Sending Request Packet - Block1 Number:{1} of {2}".format(self.reqNum, thisBlockNum + 1, len(self.block1Blocks) ))
    #             self.packetTransmitter.send(blockPacket )
    #             #return
    #             return


    #         #handle Block2
    #         if resPacket.hasBlock2:
    #             #if resPacket.block2Num != self.block2NextBlockNum
    #             if resPacket.block2Num != self.block2NextBlockNum:
    #                 self.onError(ProtocolError("Block2 packets arrived out of order"))
    #                 return

    #             #append paload to self.block2Buffer
    #             self.block2Buffer.extend(bytes(resPacket.payload))

    #             #If there are more packets:
    #             if resPacket.block2More: 
    #                 self.logger.debug("Request {0} - Received Block2 block number {1}".format(self.reqNum, resPacket.block2Num))
    #                 #request next block
    #                 self.block2NextBlockNum += 1
    #                 reqPacket = Packet(messageType=self.messageType, code=self.code, messageID=self.nextMessageID(), token=self.token,
    #                                 hostname=self.hostname, port=self.port, pathSegments=self.pathSegments, queryParams=self.queryParams,
    #                                 contentFormat=self.contentFormat, acceptFormat=self.acceptFormat, 
    #                                 block2=(self.block2NextBlockNum,False,resPacket.block2Size)  )
    #                 self.logger.debug("Request {0} - Sending Request Packet for Block2 block number:{1}".format(self.reqNum, self.block2NextBlockNum))
    #                 self.packetTransmitter.send(reqPacket )
    #                 #return
    #                 return
    #             else:
    #                 self.logger.debug("Request {0} - Received Block2 block number {1} as last block".format(self.reqNum, resPacket.block2Num))
 


    #         #send payload to callback
    #         #Return the data from block2buffer or packet payload
    #         self.logger.debug("Request {0} - Complete Returning result".format(self.reqNum))
    #         data = resPacket.payload if len(self.block2Buffer) == 0 else self.block2Buffer
    #         options = resPacket.options
    #         #self.callback(self.reqNum, data, code=resPacket.code, options=options)
    #         self.response = Response(resPacket.code, data, options, self)
    #         self.compleated = True
    #         self.packetTransmitter.close()
    #         self.done.set()

    #     elif resPacket.isRequest:
    #         self.logger.debug("Request {0} - Dropping Packet - has invalid request code".format(self.reqNum))

    #     elif resPacket.isEmpty:
    #         #Silently ignore Empty packets
    #         pass
    #         #self.logger.debug("Request {0} - Dropping Packet - has invalid empty code".format(self.reqNum))

    # # async def getResponse(self):
    # #     await self.done.wait()
    # #     return self.response