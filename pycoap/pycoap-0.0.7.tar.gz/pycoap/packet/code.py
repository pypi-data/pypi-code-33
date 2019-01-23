
import  pycoap.constants as constants

    
# ********************************************************************************************
# COAP Code
# ********************************************************************************************

class Code:

    def __init__(self, val):
        
        if isinstance(val,int):
            if val not in constants.CODE__MAP:
                raise ValueError("Invalid COAP Code")
            self._value = val
        
        elif isinstance(val,Code):
            self._value = val._value 


    def codeClass(self):
        return int( ( self._value & 0xE0 ) >> 5)

    def codeDetail(self):
        return int(self._value & 0x1F)

    def isRequest(self):
        return self.codeClass() == 0 and self.codeDetail() != 0

    def isResponse(self):
        return 2 <= self.codeClass() <=5  

    def isEmpty(self):
        return self._value == 0

    def isSuccess(self):
        return self.codeClass() == 2

    def isError(self):
        return 4 <= self.codeClass() <=  5

    def describe(self):
        return constants.CODE__MAP.get(int(self),"Undefined")



    def __str__(self):
        return "{0:01d}.{1:02d}".format(self.codeClass(),self.codeDetail())

    def __repr__(self):
        return "<Code {}>".format(str(self))

    def __bytes__(self):
        return bytes([self._value])

    def __int__(self):
        return self._value
    
    def toBytes(self):
        return bytes(self)
    
    def __eq__(self, other):
        if isinstance(other, Code):
            return self._value == other._value
        if isinstance(other, str):
            return str(self) == other
        if isinstance(other, int):
            return int(self) == other

        else:
            raise TypeError("Can not compare Code to {}".format(type(other) ) )
