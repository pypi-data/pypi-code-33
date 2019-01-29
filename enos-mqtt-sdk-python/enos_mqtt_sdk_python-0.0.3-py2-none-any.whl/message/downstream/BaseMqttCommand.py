from message.BaseAckMessage import BaseAckMessage
from core.msg.IMqttCommand import IMqttCommand

class BaseMqttCommand(BaseAckMessage, IMqttCommand):
    #__metaclass__ = ABCMeta

    def __init__(self):
        super(BaseMqttCommand, self).__init__()
        self.productKey = ''
        self.deviceKey = ''
        self.messageTopic = ''

    def getMessageId(self):
        return self.getId()

    def setMessageId(self, msgId):
        self.setId(msgId)

    def getMessageTopic(self):
        if hasattr(self, 'messageTopic'):
            return self.messageTopic

    def setMessageTopic(self, topic):
        self.messageTopic = topic

    def getProductKey(self):
        if hasattr(self, 'productKey'):
            return self.productKey

    def setProductKey(self, productKey):
        self.productKey = productKey

    def getDeviceKey(self):
        if hasattr(self, 'deviceKey'):
            return self.deviceKey

    def setDeviceKey(self, deviceKey):
        self.deviceKey = deviceKey

    def decodeToObject(self, msg):
        base = BaseMqttCommand()
        base.__dict__ = msg
        return base

    def setTopicArgs(self):
        pass

    def setCode(self, code):
        pass