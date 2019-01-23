

import asyncio
import logging
import time

import pycoap.constants as C
from pycoap.exceptions import (InvalidRequest, NotObservableError,
                               TokenMismatchError)
from pycoap.packet.code import Code
from pycoap.packet.messageType import MessageType
from pycoap.packet.packet import Packet
from pycoap.packet.token import Token
from pycoap.response import Response
from pycoap.xmitter import Xmitter as NextLayer


class Observe():

    _nextRequestNum = 0

    @classmethod
    def nextRequestNum(cls):
        cls._nextRequestNum +=1
        return cls._nextRequestNum

    @staticmethod
    async def create( destIP, destPort, messageType, code,  token=None,
                  hostname=None, pathSegments=None, queryParams=None, acceptFormat=None, ):
        """ 
        Create a Observe instance

        Essentially an async __init__(). Uses the self var to reinforce that this is an __init__.
        """
        self = Observe()
        self.reqNum = Observe.nextRequestNum()    

        if MessageType(messageType) != "CON" and MessageType(messageType) != "NON":
            raise InvalidRequest("Observe - messageType parameter must be value CON or NON")

        if not Code(code).isRequest():
            raise InvalidRequest("Observe - code parameter must be value that reflects a request")

        self.destIP = destIP
        self.destPort = destPort
        self.endpoint = (destIP,destPort)
        self.messageType = MessageType(messageType)
        self.code = Code(code)
        self.token = Token(token) if token is not None else Token(length=4)
        self.hostname = hostname if hostname is not None else destIP
        self.port = self.destPort
        self.pathSegments = pathSegments if pathSegments is not None else []
        self.queryParams = queryParams if queryParams is not None else []
        self.acceptFormat = acceptFormat

        self.compleated = False
        self.prevObserveNum = -1
        self.prevObserveTime = 0
        self.nextLayer = await NextLayer.create(self.destIP, self.destPort)

        self.logger = logging.getLogger(__name__)

        self.logger.debug("Observe {0} - Creating request coap://{1}:{2}/{3}?{4}"\
                     .format(self.reqNum,self.hostname,self.port,"/".join(self.pathSegments), "&".join(self.queryParams)))

        #Since this is not actually an __init__ return we have to return self explicitly 
        return self

    async def register(self):
        self.logger.debug("Observe {0} - Sending register packet".format(self.reqNum) )
        reqPacket = Packet(messageType=self.messageType, code=self.code,  token=self.token,
                            hostname=self.hostname, port=self.port, pathSegments=self.pathSegments, queryParams=self.queryParams,
                            payload=None, acceptFormat=self.acceptFormat, observe=C.OBSERVE_REGISTER  )
        await self.nextLayer.send(reqPacket)

 
    async def deregister(self):
        self.logger.debug("Observe {0} - Sending deregister packet".format(self.reqNum) )
        reqPacket = Packet(messageType='NON', code=self.code, token=self.token,
                            hostname=self.hostname, port=self.port, pathSegments=self.pathSegments, queryParams=self.queryParams,
                            payload=None, acceptFormat=self.acceptFormat, observe=C.OBSERVE_DEREGISTER  )
        await self.nextLayer.send(reqPacket)

    async def observe(self):
        while True:
            yield await self.receive()

    async def receive(self):
        while True:
            resPacket = await self.nextLayer.receive()

            #Make sure the token matches
            if resPacket.token != self.token:
                raise TokenMismatchError("Token mismatch error - response contained a different token from the request")

            #Make sure the response indicates an observation
            if not resPacket.hasObserve:
                raise NotObservableError("The server response indicates the resource is not observable")

            #Duplicate or old observation detection
            if self._is_old_observe(resPacket.observe):
                self.logger.debug("Observe {0} dropping old/duplicate response".format(self.reqNum))
                continue #ignore this packet and wait for the next
            else:
                self.prevObserveNum = resPacket.observe

            self.logger.debug("Observe {0} Yielding result".format(self.reqNum))
            response = Response(resPacket.code, resPacket.payload, resPacket.options)

            return response

    def stop(self):
        self.nextLayer.stop()
        pass


    def _is_old_observe(self, incommingObserveNum):
        """ 
        # Determines if the incoming observe should be  used over the existing value

        See: https://tools.ietf.org/html/rfc7641#section-3.4 for explanation
        """ 
        V1 = self.prevObserveNum
        T1 = self.prevObserveTime
        V2 = incommingObserveNum
        T2 = time.time()

        #Incoming is newer the the previous Or it 128 seconds have elapsed
        if (V1 < V2 and V2 - V1 < 2**23) or (V1 > V2 and V1 - V2 > 2**23) or (T2 > T1 + 128):
            self.prevObserveNum = V2
            self.prevObserveTime =  T2
            return False
        else:
            return True



    def __str__(self):
        return "<Observe {} - coap://{1}:{2}/{3}?{4}>" .format( self.reqNum,
                                                            self.hostname, 
                                                            self.port,"/".join(self.pathSegments), 
                                                            "&".join(self.queryParams))


    # def onResponse(self, resPacket):
    #     self.logger.debug("Observe {0} - Received Response Packet".format(self.reqNum) )

    #     if self.compleated:
    #         #Ignore the packet if Message is already compleated
    #         self.logger.warning("Observe {0} - Packate received for compleated request, probably a duplicate".format(self.reqNum))
    #         return

    #     #If packet code is in the response range
    #     if resPacket.isResponse:

    #         #Make sure the token matches
    #         if resPacket.token != self.token:
    #             #Ignore packet if Message ID does not match
    #             self.logger.error("Observe {0} - Ignoring packet with token mismatch".format(self.reqNum))
    #             return

    #         #send payload to callback
    #         #Return the data from block2buffer or packet payload
    #         self.logger.debug("Observe {0} - Complete Returning result".format(self.reqNum))
    #         data = resPacket.payload 
    #         options = resPacket.options
    #         response =  Response(resPacket.code, data, options, self)
    #         self.responseQueue.put_nowait(response)

    #     elif resPacket.isRequest:
    #         self.logger.debug("Observe {0} - Dropping Invalid Packet,  hasequest code".format(self.reqNum))

    #     elif resPacket.isEmpty:
    #         #Silently ignore Empty packets
    #         pass


    # def onError(self,exception):

    #     assert isinstance(exception, Exception)
    #     self.logger.debug("Request {0} - Received Exception {1}".format(self.reqNum, str(exception) ) )

    #     self.compleated = True
    #     self.packetTransmitter.close()
    #     #Put the error in the response queue
    #     self.responseQueue.put_nowait(exception)



    # async def xxxobserve(self):
    #     while True:
    #         resp = await self.responseQueue.get()

    #         if isinstance(resp, Exception):
    #             raise resp 
    #         else:
    #             yield resp

    
    #WORKING DEP CODE
    # async def __aiter__(self):
    #     return self

    # async def __anext__(self):
    #     resp = await self.responseQueue.get()

    #     if isinstance(resp, Exception):
    #         raise resp 
    #     else:
    #         return resp
