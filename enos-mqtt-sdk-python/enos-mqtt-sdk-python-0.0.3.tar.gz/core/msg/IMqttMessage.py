from abc import ABCMeta, abstractmethod


class IMqttMessage(object):
    __metaclass__ = ABCMeta

    @abstractmethod
    def getMessageId(self):
        pass

    @abstractmethod
    def setMessageId(self):
        pass

    @abstractmethod
    def getMessageTopic(self):
        pass

    @abstractmethod
    def setMessageTopic(self):
        pass

    @abstractmethod
    def getProductKey(self):
        pass

    @abstractmethod
    def setProductKey(self):
        pass

    @abstractmethod
    def getDeviceKey(self):
        pass

    @abstractmethod
    def setDeviceKey(self):
        pass

    @abstractmethod
    def setTopicArgs(self):
        pass