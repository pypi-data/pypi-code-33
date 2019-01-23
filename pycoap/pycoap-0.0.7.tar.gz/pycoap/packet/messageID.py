

# ********************************************************************************************
# COAP Message ID
# ********************************************************************************************

class MessageID:

    _nextMessageID = 0

    @classmethod
    def next_message_id(cls):
        cls._nextMessageID += 1
        return cls._nextMessageID


    def __init__(self,val=None):
        if val is None:
            self._value = self._int_to_bin( self.next_message_id() )
        elif isinstance(val, int):
            self._value = self._int_to_bin(val)
        elif isinstance(val, MessageID):
            self._value = val._value
        else:
            raise TypeError("{} with value {} can not be converted to a MessageID".format(type(val), str(val) ) )

    @staticmethod        
    def _int_to_bin(val):
        # convert value into 2 bytes
        # accounts for larger integers by truncating to the last two bytes
        byteLength = ( (val.bit_length() + 7 ) // 8) + 1    # Add 1 so bData will always be at least 2 bytes
        bData = val.to_bytes(byteLength, 'big' )            # convert to bytes
        return  bData[byteLength-2:]                   # Grab the last two bytes

    def __str__(self):
        return str(int(self))

    def __repr__(self):
        return str(self)

    def __int__(self):
        return int.from_bytes(self._value,"big")

    def __bytes__(self):
        return bytes(self._value)

    def toBytes(self):
        return bytes(self)

    def __eq__(self,other):
        return int(self) == int(other)

    def __hash__ (self):
        return hash( int(self) )