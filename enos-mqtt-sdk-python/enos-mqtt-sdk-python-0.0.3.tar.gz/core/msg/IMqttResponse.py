from abc import ABCMeta
from core.msg.IMqttArrivedMessage import IMqttArrivedMessage
from core.msg.IMqttAck import IMqttAck

class IMqttResponse(IMqttArrivedMessage, IMqttAck):
    __metaclass__ = ABCMeta

    pass