

import asyncio
import logging
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
        """ Initialize the client object"""

        self._nextMsgID = 0
        self.requests = {}
        self.logger = logging.getLogger(__name__)


    async def get(self,uri,acceptFormat=None):
        """ GET a coap resource 
        
        Args:
            uri (str): The uri of the resource to get
            acceptFormat (str): Request a specific content format in the response

        Raises:
            pycoap.exceptions.CoapException or a sub type of 
        
        Returns:
            response (Response) with attributes:
                code (Code): The coap status code
                payload (Payload): The data of the response
                options (dict): Dict object with fields for each coap  option in the responce 
        """
        return await self.request(uri=uri,
                     method=C.METHOD_GET,
                     payload=None,
                     acceptFormat=acceptFormat )



    async def post(self, uri, payload, acceptFormat=None, contentFormat=None):
        """ POST a coap resource 
        
        Args:
            uri (str): The uri of the resource to get
            payload (str or bytes): Data to send
            acceptFormat (str): Request a specific content format in the response
            contentFormat (str): Content format of the payload

        Raises:
            pycoap.exceptions.CoapException or a sub type of 
        
        Returns:
            response (Response) with attributes:
                code (Code): The coap status code
                payload (Payload): The data of the response
                options (dict): Dict object with fields for each coap  option in the responce 
        """
        return await self.request(uri=uri,
                     method=C.METHOD_POST,
                     payload=payload,
                     acceptFormat=acceptFormat,
                     contentFormat=contentFormat )




    async def put(self, uri, payload, acceptFormat=None, contentFormat=None):
        """ PUT a coap resource 
        
        Args:
            uri (str): The uri of the resource to get
            payload (str or bytes): Data to send
            acceptFormat (str): Request a specific content format in the response
            contentFormat (str): Content format of the payload

        Raises:
            pycoap.exceptions.CoapException or a sub type of 
        
        Returns:
            response (Response) with attributes:
                code (Code): The coap status code
                payload (Payload): The data of the response
                options (dict): Dict object with fields for each coap  option in the responce 
        """
        return await self.request(uri=uri,
                     method=C.METHOD_PUT,
                     payload=payload,
                     acceptFormat=acceptFormat,
                     contentFormat=contentFormat )




    async def delete(self,uri):
        """ GET a coap resource 
        Args:
            uri (str): The uri of the resource to get

        Raises:
            pycoap.exceptions.CoapException or a sub type of 
        
        Returns:
            response (Response) with attributes:
                code (Code): The coap status code
                payload (Payload): The data of the response
                options (dict): Dict object with fields for each coap  option in the responce 
        """
        return await self.request(uri=uri,
                     method=C.METHOD_DELETE,
                     payload=None )



    async def request(self, uri, method, payload, acceptFormat=None, contentFormat=None):
        """ Request a coap resource

         Args:
            uri (str): The uri of the resource to get
            method (int): Coap code to use in the request
            payload (str or bytes): Data to send
            acceptFormat (str): Request a specific content format in the response
            contentFormat (str): Content format of the payload

        Raises:
            pycoap.exceptions.CoapException or a sub type of 
        
        Returns:
            response (Response) with attributes:
                code (Code): The coap status code
                payload (Payload): The data of the response
                options (dict): Dict object with fields for each coap  option in the responce 
        """
        
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



    async def observe(self,uri):
        """ Observe a coap resource

         Args:
            uri (str): The uri of the resource to get

        Raises:
            pycoap.exceptions.CoapException or a sub type of 
        
        Returns:
            observation (Observe): with methods
                async register() - sends a registration request to the resource
                async deregister() - sends a deregistration request to the resource
                stop() - stop observation and close the socket
                async observe() - async generator that produces a Response object for 
                    each observation received from the server

        Example:

            from pycoap.client import Client

            client = Client()
            obs = await client.observe("coap://1.1.1.1/state")

            count = 0
            async for response in obs.observe():
                if count > 3:
                    break
                print(response.payload)
                count += 1

            obs.stop()
 
        """

        uri = URI.from_string(uri)

        try:
            destIP = socket.gethostbyname(uri.hostname)
        except socket.gaierror:
            raise NameResolutionError("Can not resolve hostname {}".format(uri.hostname))

        #Make the request packet
        obs = await Observe.create(  destIP, uri.port, 
                                messageType=C.MESSAGE_TYPE_CON, code=C.METHOD_GET, 
                                hostname=uri.hostname, pathSegments=uri.pathSegments, queryParams=uri.queryParams)

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
