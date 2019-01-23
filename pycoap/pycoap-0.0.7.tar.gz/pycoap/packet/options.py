import math #Used by Block options to convert block size to sxz

import  pycoap.constants as C

# ********************************************************************************************
# COAP Option List
# ********************************************************************************************
class OptionList(object):

    def __init__ (self):
        self._options = []

    def append(self, opt):
        if isinstance(opt, Option):
            self._options.append(opt)
        else:
            raise ValueError("Not an Option object")

    def sort(self):
        self._options.sort(key=lambda x: x._optNum)

    def __iter__(self):
        self.sort()
        for opt in self._options:
            yield opt

    def getHostname(self):
        for opt in self._options:
            if opt.optNum == C.OPTION_NUMBER_URI_HOST:
                return str(opt)
        return None

    def getPort(self):
        for opt in self._options:
            if opt.optNum == C.OPTION_NUMBER_URI_PORT:
                return int(opt)
        return C.COAP_DEFAULT_PORT

    def getPath(self):
        path = ""
        for opt in self._options:
            if opt.optNum == C.OPTION_NUMBER_URI_PATH:
                path = path + "/" + str(opt)
        return path 

    def getQuery(self):
        params = []
        for opt in self._options:
            if opt.optNum == C.OPTION_NUMBER_URI_QUERY:
                params.append(str(opt))
        strParams = "&".join(params)
        return strParams

    def getContentFormat(self):
        for opt in self._options:
            if opt.optNum == C.OPTION_NUMBER_CONTENT_FORMAT:
                return str(opt)
        return None

    def getAcceptFormat(self):
        for opt in self._options:
            if opt.optNum == C.OPTION_NUMBER_ACCEPT_FORMAT:
                return str(opt)
        return None

    def getObserve(self):
        for opt in self._options:
            if opt.optNum == C.OPTION_NUMBER_OBSERVE:
                return int(opt) 
        return None

    def getBlock1(self):
        for opt in self._options:
            if opt.optNum == C.OPTION_NUMBER_BLOCK1:
                return (opt.blockNum, opt.moreBlocks, opt.blockSize)
        return None

    def setBlock1(self,blockNum, moreBlocks, blockSize):
        found = False

        #Loop over the list looking for Block 1 option and set it
        for x in range(len(self._options)):
            if self._options[x].optNum == C.OPTION_NUMBER_BLOCK1:
                self._options[x] = Block1Option( (blockNum, moreBlocks, blockSize) )
                found = True
                break                

        #If not found append it
        if not found:
            self._options.append(Block1Option( (blockNum, moreBlocks, blockSize) ) )

    def getBlock2(self):
        for opt in self._options:
            if opt.optNum == C.OPTION_NUMBER_BLOCK2:
                return (opt.blockNum, opt.moreBlocks, opt.blockSize)
        return None

    def setBlock2(self,blockNum, moreBlocks, blockSize):
        found = False

        #Loop over the list looking for Block 1 option and set it
        for x in range(len(self._options)):
            if self._options[x].optNum == C.OPTION_NUMBER_BLOCK2:
                self._options[x] = Block2Option( (blockNum, moreBlocks, blockSize) )
                found = True
                break                

        #If not found append it
        if not found:
            self._options.append(Block2Option( (blockNum, moreBlocks, blockSize) ) )


    def getETag(self):
        for opt in self._options:
            if opt.optNum == C.OPTION_NUMBER_ETAG:
                return bytes(opt)

    def __str__(self):
        optList = ["{} Value:{}".format(opt.optName,str(opt)) for opt in self]
        return "<Options {}".format(optList)


    def toDict(self):
        return {opt.optName:str(opt) for opt in self}


    def copy(self):
        new = OptionList()
        for opt in self._options:
            new._options.append( optionFactory (opt.optNum, opt.payload ) )
        return new


# ********************************************************************************************
# COAP Option
# ********************************************************************************************
class Option(object):

    
    def __init__(self,optNum,val):

        if isinstance(optNum, int) and 0x00 <= optNum <= 0xffff:
            self._optNum = optNum
        else:
            raise ValueError("Invalid Option Number")

        self._optName = "Option-{}".format(self._optNum)


        if isinstance(val,bytes):
            self._payload = val
        elif isinstance(val,bytearray):
            self._payload = bytes(val)
        elif isinstance(val, str):
            self._payload = bytes(val,'utf-8')
        elif isinstance(val, int):
            byteLen = (int.bit_length() + 7) // 8
            self._payload = int.to_bytes(byteLen, 'big')
        else:
            raise ValueError("Invalid Option Payload Data")

    @property
    def number(self):
        return self._optNum

    @property
    def name(self):
        return self._optName


    @property
    def optNum(self):
        return self._optNum

    @property
    def optName(self):
        return self._optName

    @property
    def payload(self):
        return self._payload

    @property
    def length(self):
        return len(self._payload)

    def toString(self):
        return str(self)

    def getValue(self):
        return bytes(self)

    def __str__(self):
        return str(self._payload)

    def __repr__(self):
        return "<{} {}>".format(self.__class__.__name__, str(self))
        
    def __bytes__(self):
        return bytes(self._payload)


    def to_bytes(self, prevOptNum):
  
        #Build The Header
        data = bytearray(1)
        delta = self.optNum - prevOptNum
        
        if self.optNum > 65535:
            raise ValueError("Invalid Option Number")
        if delta >= 269:
            data[0] = 14 << 4
            data.extend( (delta - 269).to_bytes(2,"big") )
        elif delta >= 13:
            data[0] = 13 << 4
            data.extend( (delta -  13).to_bytes(1,"big") )
        else:
            data[0] = delta << 4

        if self.length > 65535:
            raise ValueError("Option data exceeds maximum length")
        if self.length >= 269:
            data[0] |=  14
            data.extend( (self.length - 269).to_bytes(2,"big") ) 
        elif self.length >= 13:
            data[0] |= 13
            data.extend( (self.length -  13).to_bytes(1,"big") ) 
        else:
            data[0] |= self.length

        #Add the payload    
        data.extend(self._payload)

        #Return bytes
        return bytes(data)

class BaseStringOption(Option):
    
    def __init__(self,val):
        if isinstance(val, bytes):
            self._payload = val
        elif isinstance( val, str ):
            self._payload = bytes(val,'ascii')
        else:
            raise ValueError("Invalid {0} value: {1}".format(self.optName, str(val)) )

    def __str__(self):
        return self._payload.decode('utf-8')

    def getValue(self):
        return str(self)


class BaseIntOption(Option):
    _maxByteLength = 0

    @staticmethod        
    def _int_to_bin(val,length):
        """ 
        convert value into length long bytes object
        accounts for larger integers by truncating to the last length bytes
        """
        byteLength = ( (val.bit_length() + 7 ) // 8) + 1    # Add 1 so bData will always be at least 2 bytes
        bData = val.to_bytes(byteLength, 'big' )            # convert to bytes
        return  bData[byteLength-length:]                   # Grab the last length bytes
    
    
    def __init__(self,val):
        if isinstance ( val, bytes):
            if len(val) > self._maxByteLength:
                raise ValueError("Value " + str(val) + " is to large for " + self._optName)                    
            self._payload = val

        elif isinstance ( val, int):
            self._payload = self._int_to_bin(val, self._maxByteLength)

        else:
            raise ValueError("Invalid " + self._optName + " value:" + str(val))

    def __int__(self):
        return int.from_bytes(self._payload, "big")

    def __str__(self):
        return str(int(self))

    def toInt(self):
        return int(self)

    def getValue(self):
        return int(self)

    def __eq__(self, other):
        if isinstance(other, BaseIntOption):
            return self._payload == other._payload
        elif isinstance(other, str):
             return str(self) == other
        elif isinstance(other,int):
            return int(self) == other
        else:
            raise TypeError("Can not compare {} to {}".format( type(other), type(self) ) )   


class BaseFormatOption(Option):
    _maxByteLength = 2
    
    def __init__(self,val):
        if isinstance ( val, bytes):
            if len(val) > self._maxByteLength:
                raise ValueError("Value " + str(val) + " is to large for " + self._optName)                    
            self._payload = val

        elif isinstance ( val, int):
            byteLength = (val.bit_length() + 7) // 8
            if byteLength > self._maxByteLength:
                raise ValueError("Value " + str(val) + " is to large for " + self._optName)                    
            self._payload = val.to_bytes(byteLength,"big")

        elif isinstance ( val, str):
            #Reverse dict sarch gets a key for a value
            i = [key for key,value in C.FORMAT__MAP.items() if value == val]

            if len(i) == 1:
                self._payload= i[0].to_bytes(1,"big")
            else:
                raise ValueError("Invalid " + self._optName + " value:" + val)
        
        elif isinstance (val, BaseFormatOption):
            self._payload = val._payload

        else:
            raise ValueError("Invalid " + self._optName + " value:" + str(val))

    def __int__(self):
        return int.from_bytes(self._payload, "big")


    def toInt(self):
        return int(self)


    def __str__(self):
        return C.FORMAT__MAP.get(int(self),"Unknown Format")

    def __eq__(self,other):
        if isinstance(other, int):
            return int(self) == other
        elif isinstance(other, str):
            return str(self) == other
        else:
            raise TypeError("Can not compare {} to {}".format( type(self), type(other) ))


    def getValue(self):
        return str(self)


class BaseBlockOption(Option):

    def __init__ (self, val):
        assert isinstance(val, bytes) or ( isinstance(val, tuple) and len(val) == 3 )

        if isinstance(val,bytes):
            self._payload = val 
        else:
            blockNum,moreBlocks,blockSize = val
            self._payload = self.payload_from_values(blockNum,moreBlocks,blockSize)

    @staticmethod
    def payload_from_values(blockNum, moreBlocks, blockSize):
        assert 0 <= blockNum <= 2**20 , "must be between 0 and 2**20"
        assert 16 <= blockSize <= 1024, "must betetwen 16 and 1024"
        assert blockSize & ( blockSize -1 ) == 0, "must be a power of 2"

        szx = int(math.log(blockSize,2)) - 4
        num = blockNum << 4
        byteLen = (num.bit_length() + 7) // 8
        byteLen = 1 if byteLen == 0 else byteLen
        payload = bytearray(num.to_bytes(byteLen, 'big'))
        payload[byteLen -1] |= int(bool(moreBlocks)) << 3
        payload[byteLen -1] |= szx

        return bytes(payload)
 
    def __str__(self):
        return "num:{0} more:{1} size:{2}".format(self.blockNum, self.moreBlocks, self.blockSize)

    def getValue(self):
        return str(self)

    @property
    def blockNum(self):
        return int.from_bytes(self._payload, "big") >> 4

    @property
    def moreBlocks(self):
        byte = self._payload[len(self._payload)-1] 
        return bool(( byte & 0x08 ) >> 3)

    @property
    def blockSize(self):
        byte = self._payload[len(self._payload)-1] 
        szx =  byte & 0x07 
        return  2 ** (szx + 4)


class HostOption(BaseStringOption):
    _optNum = C.OPTION_NUMBER_URI_HOST
    _optName = "URI-Host"

class PortOption(BaseIntOption):
    _optNum = C.OPTION_NUMBER_URI_PORT
    _optName = "URI-Port"
    _maxByteLength = 2

 
class PathOption(BaseStringOption):
    _optNum = C.OPTION_NUMBER_URI_PATH
    _optName = "URI-Path"



class QueryOption(BaseStringOption):
    _optNum = C.OPTION_NUMBER_URI_QUERY
    _optName = "URI-Query"


class ContentFormatOption(BaseFormatOption):
    _optNum = C.OPTION_NUMBER_CONTENT_FORMAT
    _optName = "Content-Format"

class AcceptFormatOption(BaseFormatOption):
    _optNum = C.OPTION_NUMBER_ACCEPT_FORMAT
    _optName = "Accept-Format"

class Block1Option(BaseBlockOption):
    _optNum = C.OPTION_NUMBER_BLOCK1
    _optName = "Block1"

class Block2Option(BaseBlockOption):
    _optNum = C.OPTION_NUMBER_BLOCK2
    _optName = "Block2"

class ObserveOption(BaseIntOption):
    _optNum = C.OPTION_NUMBER_OBSERVE
    _optName = "Observe"
    _maxByteLength = 3

    @property
    def isRegister(self):
        return int(self) == 0

    @property
    def isDeregister(self):
        return int(self) == 1

    @property
    def isNotification(self):
        return int(self) > 1



class ETagOption(Option):
    _optNum = C.OPTION_NUMBER_ETAG
    _optName = "ETag"

    def __init__(self,val):

        # if isinstance(optNum, int) and 0x00 <= optNum <= 0xffff:
        #     self._optNum = optNum
        # else:
        #     raise ValueError("Invalid Option Number")

        if isinstance(val,bytes):
            self._payload = val
        elif isinstance(val,bytearray):
            self._payload = bytes(val)
        elif isinstance(val, str):
            self._payload = bytes(val,'utf-8')
        elif isinstance(val, int):
            byteLen = (int.bit_length() + 7) // 8
            self._payload = int.to_bytes(byteLen, 'big')
        else:
            raise ValueError("Invalid Option Payload Data")



def optionFactory(optNum,payload):
    if   optNum == C.OPTION_NUMBER_URI_HOST: return HostOption(payload)
    elif optNum == C.OPTION_NUMBER_OBSERVE: return ObserveOption(payload)
    elif optNum == C.OPTION_NUMBER_URI_PORT: return PortOption(payload)
    elif optNum == C.OPTION_NUMBER_URI_PATH: return PathOption(payload)
    elif optNum == C.OPTION_NUMBER_CONTENT_FORMAT: return ContentFormatOption(payload)
    elif optNum == C.OPTION_NUMBER_URI_QUERY: return QueryOption(payload)
    elif optNum == C.OPTION_NUMBER_ACCEPT_FORMAT: return AcceptFormatOption(payload)
    elif optNum == C.OPTION_NUMBER_BLOCK2: return Block2Option(payload) 
    elif optNum == C.OPTION_NUMBER_BLOCK1: return Block1Option(payload) 
    elif optNum == C.OPTION_NUMBER_ETAG: return ETagOption(payload) 
    else: return Option(optNum,payload)




