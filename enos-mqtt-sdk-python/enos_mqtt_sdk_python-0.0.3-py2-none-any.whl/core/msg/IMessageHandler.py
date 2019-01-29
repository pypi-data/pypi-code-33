from abc import ABCMeta, abstractmethod
from IMqttArrivedMessage import IMqttArrivedMessage
from IMqttDeliveryMessage import IMqttDeliveryMessage
from message.downstream.BaseMqttReply import BaseMqttReply


class IMessageHandler(IMqttArrivedMessage, IMqttDeliveryMessage):
    # __metaclass__ = ABCMeta

    # @abstractmethod
    def onMessage(self, arrivedMessage, argList, msgHandler=None):
        reply = BaseMqttReply()
        if msgHandler is None:
            reply.setCode(1101)
            reply.setMessage('downstream command handler not registered')
            return reply
        try:
            msgHandler(arrivedMessage, reply)
            return reply
        except Exception as e:
            reply.setCode(2000)
            reply.setMessage('msgHandler execute failed:%s' % e.message)
            return reply

    def getDeviceKey(self):
        pass

    def getProductKey(self):
        pass

    def getMessageTopic(self):
        pass

    def getMessageId(self):
        pass

    def setDeviceKey(self):
        pass

    def setMessageId(self):
        pass

    def setProductKey(self):
        pass

    def setTopicArgs(self):
        pass