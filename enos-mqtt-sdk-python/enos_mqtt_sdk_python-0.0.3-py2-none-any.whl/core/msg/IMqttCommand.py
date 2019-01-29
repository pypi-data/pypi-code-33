from abc import ABCMeta
from core.msg.IMqttArrivedMessage import IMqttArrivedMessage
from core.msg.IMqttAck import IMqttAck

class IMqttCommand(IMqttArrivedMessage, IMqttAck):
    __metaclass__ = ABCMeta

    pass