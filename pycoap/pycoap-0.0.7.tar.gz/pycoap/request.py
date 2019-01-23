

import asyncio
import logging

# import pycoap.constants as C
from pycoap.exceptions import InvalidRequest, TokenMismatchError
from pycoap.packet.code import Code
from pycoap.packet.messageType import MessageType
from pycoap.packet.packet import Packet
from pycoap.packet.payload import Payload
from pycoap.packet.token import Token
from pycoap.response import Response
#from pycoap.xmitter import Xmitter as NextLayer
from pycoap.block2 import Block2 as NextLayer



class Request(object):
    """ 
    Initiates a request and returns a response. Primary function is to convert a bunch 
    parameters to packet and send it down the stack
    """

    _requestNum = 0

    @classmethod
    def nextRequestNum(cls):
        cls._requestNum +=1
        return cls._requestNum


    @staticmethod
    async def create(   destIP, destPort, messageType, code,  token=None,
                        hostname=None, pathSegments=None, queryParams=None,
                        contentFormat=None, acceptFormat=None, payload=None,
                        block1Size=None):
        """ 
        Create a Request instance

        Essentially an async __init__(). Uses the self var to reinforce that this is an __init__.
        """
        self = Request ()
        self.reqNum = Request.nextRequestNum()


        if MessageType(messageType) != "CON" and MessageType(messageType) != "NON":
            raise InvalidRequest("Request - messageType parameter must be value CON or NON")

        if not Code(code).isRequest:
            raise InvalidRequest("Request - code parameter must reflect a request")

        self.destIP = destIP
        self.destPort = destPort
        self.messageType = MessageType(messageType)
        self.code = Code(code)
        self.token = Token(token) if token is not None else Token(length=4)
        self.payload = Payload(payload)
        self.hostname = hostname if hostname is not None else destIP
        self.port = self.destPort
        self.pathSegments = pathSegments if pathSegments is not None else []
        self.queryParams = queryParams if queryParams is not None else []
        self.contentFormat = contentFormat
        self.acceptFormat = acceptFormat

        self.compleated = False


        self.nextLayer = await NextLayer.create(self.destIP, self.destPort)

        self.logger = logging.getLogger(__name__)

        self.logger.debug("Request {0} - Creating request coap://{1}:{2}/{3}?{4}"\
                     .format(self.reqNum,self.hostname,self.port,"/".join(self.pathSegments), "&".join(self.queryParams)))

        #Since this is not actually an __init__ explicitly return self
        return self

    async def send(self):
        """ Sends a packet """
        reqPacket = Packet( messageType=self.messageType, 
                            code=self.code, 
                            token=self.token,
                            hostname=self.hostname, 
                            port=self.port, 
                            pathSegments=self.pathSegments, 
                            queryParams=self.queryParams,
                            payload=self.payload, 
                            contentFormat=self.contentFormat, 
                            acceptFormat=self.acceptFormat )

        await self.nextLayer.send(reqPacket)



    async def receive(self):
        """ Receives a packet """
        resPacket = await self.nextLayer.receive()

        #Make sure the token matches
        if resPacket.token != self.token:
            raise TokenMismatchError("Token mismatch error - responce contained a different token from the request")

        self.logger.debug("Request {0} - Complete. Returning result".format(self.reqNum))
        response = Response(resPacket.code, resPacket.payload, resPacket.options)
        self.stop()

        return response

    def stop(self):
        self.compleated = True
        self.nextLayer.stop()

    def __repr__(self):
        return "Request {0} coap://{1}:{2}/{3}?{4}" .format(self.reqNum,
                                                            self.hostname,
                                                            self.port,
                                                            "/".join(self.pathSegments),
                                                            "&".join(self.queryParams) )

    def __str__(self):
        return repr(self)


