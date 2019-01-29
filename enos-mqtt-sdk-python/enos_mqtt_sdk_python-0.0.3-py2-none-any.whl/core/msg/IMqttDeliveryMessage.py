from abc import ABCMeta
from core.msg.IMqttMessage import IMqttMessage


class IMqttDeliveryMessage(IMqttMessage):
    __metaclass__ = ABCMeta

    def check(self):
        pass

    def encode(self):
        pass

    def getQos(self):
        pass

    def setMessageTopic(self, topic):
        pass
