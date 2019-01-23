

import  pycoap.constants as constants
# ********************************************************************************************
# COAP Message Type
# ********************************************************************************************


class MessageType:

    def __init__(self,val):
        t = str(val).lower()

        if t=="0" or t=="con" or t=="confirmable" or t=="confirmable (0)":
                self._value = constants.MESSAGE_TYPE_CON
        elif t=="1" or t=="non" or t=="noncon" or t=="non-confirmable"  or t=="non-confirmable (1)":
                self._value = constants.MESSAGE_TYPE_NONCON
        elif t=="2" or t=="ack" or t=="acknowledgement" or t=="acknowledgement (2)":
                self._value = constants.MESSAGE_TYPE_ACK
        elif t=="3" or t=="rst" or t=="reset"  or t=="reset (4)":
                self._value = constants.MESSAGE_TYPE_RESET
        else:
            raise ValueError("Invalid COAP Message Type: " + str(val) )

        #self._type = type


    def __str__(self):
        if self._value == constants.MESSAGE_TYPE_CON:
            string = "Confirmable"
        elif self._value == constants.MESSAGE_TYPE_NONCON:
            string = "Non-Confirmable"
        elif self._value == constants.MESSAGE_TYPE_ACK:
            string =  "Acknowledgement"
        elif self._value == constants.MESSAGE_TYPE_RESET:
            string =  "Reset"
        # else:
        #     val =  "Unknown"
        return "{0} ({1})".format(string,self._value)

    def __repr__(self):
        if self._value == constants.MESSAGE_TYPE_CON:
            return "CON"
        elif self._value == constants.MESSAGE_TYPE_NONCON:
            return "NON"
        elif self._value == constants.MESSAGE_TYPE_ACK:
            return "ACK"
        elif self._value == constants.MESSAGE_TYPE_RESET:
            return "RST"

    def __int__(self):
        return self._value



    def toString(self):
        return str(self)

    def toInt(self):
        return int(self)

    def __eq__(self,other):
        if isinstance(other,str):
            return repr(self) == other
        elif isinstance(other,int):
            return int(self) == int(other)
        elif isinstance(other, MessageType):
            return int(self) == int(other)
        else:
            raise TypeError("Cannont compare messageType to type {1}".format(type(other)))


