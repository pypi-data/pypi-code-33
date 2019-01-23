

from ipaddress import ip_address

import pycoap.constants as C
from pycoap.buffer import Buffer
from pycoap.packet.code import Code
from pycoap.packet.messageID import MessageID
from pycoap.packet.messageType import MessageType
from pycoap.packet.options import (AcceptFormatOption, Block1Option,
                                   Block2Option, ContentFormatOption,
                                   HostOption, ObserveOption, OptionList,
                                   PathOption, PortOption, QueryOption,
                                   optionFactory)
from pycoap.packet.payload import Payload
from pycoap.packet.token import Token


# ********************************************************************************************
# COAP Packet
# ********************************************************************************************
class Packet:

    def __init__( self, messageType, code, messageID=None, token=None, payload="",
                 hostname=None, port=None, pathSegments=None, queryParams=[], 
                 contentFormat=None, acceptFormat=None, 
                 observe=None, block1=None, block2=None):
        

        self._messageType = MessageType(messageType)
        self._code = Code(code)
        self._messageID = MessageID(messageID)
        self._token = Token(token)
        self._payload = Payload(payload)

        self._options = OptionList()

        if hostname is not None:
            self._options.append(HostOption(hostname))

        if port is not None:
            self._options.append(PortOption(port))

        if pathSegments is not None:
            if isinstance(pathSegments,list):
                for segment in pathSegments:
                    self._options.append(PathOption(segment))
            else:
                raise TypeError("pathSegments must be a list object")    

        if queryParams is not None:
            if isinstance(queryParams,list):
                for param in queryParams:
                    self._options.append(QueryOption(param))
            else:
                raise TypeError("queryParams must be a list object")    

        if contentFormat is not None:
            self._options.append(ContentFormatOption(contentFormat))

        if acceptFormat is not None:
            self._options.append(AcceptFormatOption(acceptFormat))

        if observe is not None:
            self._options.append(ObserveOption(observe))

        if block1 is not None:
            self._options.append(Block1Option(block1))

        if block2 is not None:
            self._options.append(Block2Option(block2))

    def copy(self):
        """Creates a deep copy of the packet"""
        copy = Packet(messageType=self.messageType, 
                      code=self.code, 
                      messageID=self.messageID, 
                      token=self.token, 
                      payload=self.payload)
        copy._options = self._options.copy()
        return copy

    def new(self):
        """Create a deep copy of the packet, but with a new messageID"""
        copy = self.copy()
        copy._messageID = MessageID()
        return copy        

    @property
    def messageType(self):
        return self._messageType

    @property
    def code(self):
        return self._code
    
    @property
    def isRequest(self):
        return self.code.isRequest()

    @property
    def isResponse(self):
        return self.code.isResponse()

    @property
    def isEmpty(self):
        return self.code.isEmpty()
        
    @property
    def messageID(self):
        return self._messageID


    @property
    def token(self):
        return self._token

    @property
    def payload(self):
        return self._payload

    def setPayload(self, val):
        self._payload = Payload(val)

    @property
    def hostname(self):
        return self._options.getHostname()

    @property
    def hostnameIsIPAddress(self):
        try:
            ip_address(self.hostname)
        except ValueError:
            return False
        return True

    @property
    def port(self):
        return self._options.getPort()

    @property
    def path(self):
        return self._options.getPath()

    @property
    def query(self):
        return self._options.getQuery()

    @property
    def contentFormat(self):
        return self._options.getContentFormat()

    @property
    def acceptFormat(self):
        return self._options.getAcceptFormat()

    @property
    def observe(self):
        return self._options.getObserve()

    @property
    def hasObserve(self):
        return self.observe is not None

    @property
    def hasBlock1(self):
        return self._options.getBlock1() is not None

    @property
    def block1(self):
        return self._options.getBlock1()

    def setBlock1(self, blockNum, moreBlocks, blockSize):
        self._options.setBlock1(blockNum, moreBlocks, blockSize)

    @property
    def block1Num(self):
        blockVal = self._options.getBlock1() 
        if blockVal is not None:
            return blockVal[0]

    @property
    def block1More(self):
        blockVal = self._options.getBlock1() 
        if blockVal is not None:
            return blockVal[1]

    @property
    def block1Size(self):
        blockVal = self._options.getBlock1() 
        if blockVal is not None:
            return blockVal[2]


    @property
    def hasBlock2(self):
        return self._options.getBlock2() is not None

    def setBlock2(self, blockNum, moreBlocks, blockSize):
        self._options.setBlock2(blockNum, moreBlocks, blockSize)

    @property
    def block2(self):
        return self._options.getBlock2()

    @property
    def block2Num(self):
        blockVal = self._options.getBlock2() 
        if blockVal is not None:
            return blockVal[0]

    @property
    def block2More(self):
        blockVal = self._options.getBlock2() 
        if blockVal is not None:
            return blockVal[1]

    @property
    def block2Size(self):
        blockVal = self._options.getBlock2() 
        if blockVal is not None:
            return blockVal[2]

    @property
    def etag(self):
        return self._options.getETag() 

    @property
    def options(self):
        return self._options

    def getOptions(self):
        optList = [opt for opt in self._options]
        return optList

    def __eq__(self, other):
        return self.toBytes() == other.toBytes()

    def __repr__(self):
        return "<Packet type:{} code:{} id:{} options:{}>".format(  self.messageType,
                                                                    self.code,
                                                                    self.messageID,
                                                                    self.options)

    def __bytes__(self):

        data = bytearray()

        # Version, messageType and Token Length
        bit = 0x00
        bit |=  C.COAP_VERSION  << 6
        bit |=  int(self._messageType)  << 4
        bit |=  len(self._token)  
        data.append(bit)

        # Code
        data.extend( bytes(self._code) )

        # Message ID
        data.extend( bytes(self._messageID) )

        # Token
        data.extend( bytes(self._token) )

        # Options and Payload are not included with an empty code packet
        if self.code != C.CODE_EMPTY:
            #Options
            prevOptNum = 0
            for opt in self._options:   
                if opt.optNum == C.OPTION_NUMBER_URI_HOST and self.hostnameIsIPAddress:
                    pass # Don't include Host URI option 
                else:
                    data.extend(opt.to_bytes(prevOptNum) )
                    prevOptNum = opt.optNum

            #Payload
            if len(self._payload) > 0:
                data.append(0xFF) #The start of payload markder
                data.extend( bytes(self._payload))

        return bytes(data)

    def toBytes(self):
        return bytes(self)


    @classmethod
    def from_bytes(cls, data):
        if not isinstance(data, bytes) and not isinstance(data, bytearray):
            raise TypeError("data is not a bytes object")

        data = Buffer(data)

        if len(data) < 4: #Min lengh of a packet with no payload, zero options and zero lenght token    
            raise ValueError("Invalid packet - Not Long Enough")

        #Start parsing
        byte = data.readInt(1)
        version = ( byte & 0xC0 ) >> 6
        messageType = ( byte & 0x30 ) >> 4
        tokenLength = byte & 0x0F

        #print(version)
        if version != 1:
            raise ValueError("Invalid packet version")
        code = data.readInt(1)
        messageID = data.readInt(2)
        token = data.read(tokenLength)

        packet = cls(messageType=messageType, code=code, messageID=messageID, token=token )

        prevOptNum = 0
       
        while data.readable():
            byte = data.readInt(1) 

            #Check for payload marker
            if byte == 0xFF:
                break 

            optDelta = (byte & 0xF0) >> 4
            optLen = byte & 0x0F

            if optDelta == 13:    optNum = data.readInt(1) + prevOptNum + 13
            elif optDelta == 14:  optNum = data.readInt(2) + prevOptNum + 269
            else:                 optNum = optDelta + prevOptNum

            if optLen == 13:      optLen = data.readInt(1) + 13
            elif optLen == 14:    optLen = data.readInt(2) + 269

            optPayload = data.read(optLen)

            #Append the option
            packet._options.append(optionFactory(optNum,optPayload))

            #update previous option number
            prevOptNum = optNum
 
        #Read the packet payload
        packet._payload= Payload(data.readAll())

        return packet



    def dumpToStr(self):
        dump =  "COAP Packet:\n"
        dump += "     MessageType:      %s\n" % self._messageType
        dump += "     Code:             %s\n" % self._code
        dump += "     MessageID:        %s\n" % self._messageID
        dump += "     Token:            %s\n" % self._token
        for opt in self._options:
            dump += "     Option:           {1} ({0}) - {2}\n".format(opt.number,opt.name,str(opt) ) 
        dump += "     Payload:          %s\n" % self._payload

        return dump

    def dump(self):
        print(self.dumpToStr())
