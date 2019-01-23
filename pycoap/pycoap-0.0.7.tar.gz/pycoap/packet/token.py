from random import randint

# ********************************************************************************************
# COAP Token
# ********************************************************************************************


class Token:

    @property
    def length(self):
        return len(self._value)


    def __init__(self, value=None, length=0 ):

 
        if isinstance(value, Token):
            assert len(value) <= 8
            self._value = bytes(value)  #Copy the token

        elif isinstance(value,str) and len(value) <= 8:
            assert len(value) <= 8
            self._value = value.encode()

        elif isinstance(value, bytes):
            assert len(value) <= 8
            self._value = value         

        else:
            assert 0 <= length <= 8
            self.setRandom(length)
        
    def setRandom(self,length):
        self._value = bytearray(length)
        for x in range(length):
            self._value[x] = randint(0,255)

    def __len__(self):
        return self.length

    def __str__(self):
        if(len(self._value)==0):
            string = "(zero length token)"
        else:
            string = ""
            for byte in range(len(self._value)):
                string += "0x{0:x} ".format(self._value[byte])

        return string

    def __repr__(self):
        return "<Token {}>".format(str(self))
    
    
    def __bytes__(self):
        return bytes(self._value)

    def  toBytes(self):
        return bytes(self)

    def __eq__(self,other):
        if isinstance(other,Token):
            return self._value == other._value
        elif isinstance(other,bytes):
            return self._value == other
        elif isinstance(other,str):
            return self._value == other.encode()
        else:
            raise TypeError("Cannot compare Token to {}".format(type(other)))



