from abc import ABCMeta, abstractmethod


class IMqttAck(object):
    __metaclass__ = ABCMeta

    @abstractmethod
    def setCode(self, code):
        pass

    @abstractmethod
    def setMessage(self, message):
        pass