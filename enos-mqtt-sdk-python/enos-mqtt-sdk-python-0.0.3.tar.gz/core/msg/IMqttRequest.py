from abc import ABCMeta, abstractmethod
from core.msg.IMqttDeliveryMessage import IMqttDeliveryMessage
from core.msg.IAnswerable import IAnswerable

class IMqttRequest(IMqttDeliveryMessage, IAnswerable):
    __metaclass__ = ABCMeta

    @abstractmethod
    def getVersion(self):
        pass

    @abstractmethod
    def setVersion(self, version):
        pass
