


# ********************************************************************************************
# COAP Message ID
# ********************************************************************************************

class Buffer(object):

    def __init__(self,val=None):
        self._pos = 0
        
        if isinstance(val,bytes):
            self._buffer = val

        elif isinstance(val,bytearray):
            self._buffer = bytes(val)

        elif isinstance(val, str):
            self._buffer = bytes(val,'utf-8')

        elif isinstance(val, int):
            byteLen = (int.bit_length() + 7) // 8
            self._buffer = int.to_bytes(byteLen, 'big')

        elif isinstance(val,Buffer):
            self._buffer = val._buffer

        elif val is None:
            self._buffer = bytes()
        else:
            raise ValueError("Cannot make buffer from " + str(val) )

    def readReset(self):
        self._pos = 0

    def read(self, byteCount):
        if self._pos + byteCount <= len(self._buffer):
            start = self._pos
            end = self._pos + byteCount
            self._pos = end
            return self._buffer[start:end]
        else:
            raise IndexError("Cannot read specified number of bytes")

    def readInt(self, byteCount):
        if self._pos + byteCount <= len(self._buffer):
            return int.from_bytes( self.read(byteCount), "big" )
        else:
            raise IndexError("Cannot read specified number of bytes")

    def readAll(self):
        start = self._pos
        self._pos = 0
        return self._buffer[start:]

    def readable(self):
        return self._pos < len(self._buffer)

    def __str__(self):
        return self._buffer.decode("utf-8")

    def __repr__(self):
        if len(self) <= 32:
            return "<{} '{}'>".format(self.__class__.__name__, str(self) )
        else:
            return "<{} '{}...' length:{}>".format(self.__class__.__name__, str(self)[:32], len(self) )

            
    def __bytes__(self):
        return self._buffer

    def __len__(self):
        return len(self._buffer)

    def __getitem__(self,i):
        return  self._buffer[i]

    def __getslice__(self,i,j):
        return Buffer(self._buffer[i:j])

    def toString(self):
        return str(self)

    def toBytes(self):
        return bytes(self)
    
    def decode(self,encoding,**kwargs):
        return self._buffer.decode(**kwargs)

    def extend(self,val):
        if isinstance(val,bytes) or isinstance(val,bytearray) or isinstance(val,Buffer):
            array = bytearray(self._buffer)
            array.extend(val)
            self._buffer = array
        else:
            raise TypeError("Can not extend with type {}".format(type(val)))


    def __eq__(self, other):
        if isinstance(other,str):
            return str(self) == other
        if isinstance(other,bytes):
            return bytes(self) == other
        else:
            raise TypeError("Can not compare {} to {}".format( type(self), type(other) ))


