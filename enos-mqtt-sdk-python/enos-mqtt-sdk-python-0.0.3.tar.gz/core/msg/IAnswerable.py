from abc import ABCMeta, abstractmethod

class IAnswerable(object):
    __metaclass__ = ABCMeta

    @abstractmethod
    def getAnswerType(self):
        pass

    @abstractmethod
    def getAnswerTopic(self):
        pass