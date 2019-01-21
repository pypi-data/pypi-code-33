

import asyncio
import pycoap.logging as logging
import socket
from urllib.parse import urlsplit

import pycoap.constants as C
from pycoap.exceptions import NameResolutionError
from pycoap.observe import Observe
# from pycoap.packet.packet import Packet
# from pycoap.packet.token import Token
from pycoap.request import Request


class URI(object):
    def __init__(self,hostname,port,pathSegments,queryParams):
        self.hostname = hostname
        self.port = port
        self.pathSegments = pathSegments
        self.queryParams = queryParams

    @classmethod
    def from_string(cls,uri):
        hostname = ""
        port = C.COAP_DEFAULT_PORT
        pathSegments = []
        queryParams = []

        splituri = urlsplit(uri)

        if (splituri.hostname) is not None:
            hostname=splituri.hostname

        if splituri.port is not None:
            port=splituri.port
 
        if splituri.path != "" and splituri.path != "/":
            pathSegments = splituri.path[1:].split("/") #Remove leading / and split
 
        if splituri.query != "" and splituri.query != "?":
            queryParams = splituri.query.split("&") #split
 
        return cls(hostname,port,pathSegments,queryParams)



class Client(object):

    def __init__(self):

        self._nextMsgID = 0
        self.requests = {}
        self.logger = logging.getLogger(__name__)


    async def get(self,uri,acceptFormat=None):
        return await self.request(uri=uri,
                     method=C.METHOD_GET,
                     payload=None,
                     acceptFormat=acceptFormat )

    async def post(self, uri, payload, acceptFormat=None, contentFormat=None):
        return await self.request(uri=uri,
                     method=C.METHOD_POST,
                     payload=payload,
                     acceptFormat=acceptFormat,
                     contentFormat=contentFormat )

    async def put(self, uri, payload, acceptFormat=None, contentFormat=None):
        return await self.request(uri=uri,
                     method=C.METHOD_PUT,
                     payload=payload,
                     acceptFormat=acceptFormat,
                     contentFormat=contentFormat )

    async def delete(self, uri, payload=None, acceptFormat=None, contentFormat=None):
        return await self.request(uri=uri,
                     method=C.METHOD_DELETE,
                     payload=payload,
                     acceptFormat=acceptFormat,
                     contentFormat=contentFormat )


    async def request(self, uri, method, payload, acceptFormat=None, contentFormat=None):
        uri = URI.from_string(uri)

        try:
            destIP = socket.gethostbyname(uri.hostname)
        except socket.gaierror:
            raise NameResolutionError("Can not resolve hostname {}".format(uri.hostname))

        #Make the request packet
        req = await Request.create( destIP, uri.port, messageType=C.MESSAGE_TYPE_CON, code=method,
                                    hostname=uri.hostname, pathSegments=uri.pathSegments, 
                                    queryParams=uri.queryParams, contentFormat=contentFormat, 
                                    acceptFormat=acceptFormat, payload=payload)
        await req.send()
        return await req.receive()



    async def observe(self,uri, acceptFormat=None):
        uri = URI.from_string(uri)

        try:
            destIP = socket.gethostbyname(uri.hostname)
        except socket.gaierror:
            raise NameResolutionError("Can not resolve hostname {}".format(uri.hostname))

        #Make the request packet
        obs = await Observe.create(  destIP, uri.port, 
                                messageType=C.MESSAGE_TYPE_CON, code=C.METHOD_GET, 
                                hostname=uri.hostname, pathSegments=uri.pathSegments, queryParams=uri.queryParams, 
                                acceptFormat=acceptFormat)

        return obs




    # def ping(self,hostname,callback, port=None):

    #     port = C.COAP_DEFAULT_PORT if port is None else port

    #     ip = self.udpClass.getIP(hostname)
    #     if ip is None:
    #         info = {"error":C.ERROR_DNS, "description":C.ERROR_MAP[C.ERROR_DNS]}
    #         callback(None,info)
    #         return        

    #     req = Request(self.udpClass, self.handlePingResponse, ip, port,
    #                   messageType=C.MESSAGE_TYPE_CON, code=C.CODE_EMPTY)
    #     self.requests[req.reqNum] = (req, callback)
    
    # def handlePingResponse(self,reqNum, data=None, code=None, contentFormat=None, etag=None, observe=None, error=None):
    #     self.logger.debug("Client: Received Ping response")

    #     if not isinstance(error, Error):
    #         raise RuntimeError("handlePingResponce is susposed to receive an error object")

    #     (req, appCallback) = self.requests[reqNum]


    #     if error.code == C.ERROR_RESET:
    #         appCallback(None,{})
    #     else:
    #         info = {"error":error.code, "description": error.message}
    #         appCallback(None,info)
