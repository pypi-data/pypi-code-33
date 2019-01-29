from message.BaseAckMessage import BaseAckMessage
from core.msg.IMqttResponse import IMqttResponse

class BaseMqttResponse(BaseAckMessage, IMqttResponse):
    #__metaclass__ = ABCMeta

    def __init__(self):
        super(BaseMqttResponse, self).__init__()
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
        if hasattr(self, 'devicekey'):
            return self.deviceKey

    def setDeviceKey(self, deviceKey):
        self.deviceKey = deviceKey

    def decodeToObject(self, msg):
        base = BaseMqttResponse()
        base.__dict__ = msg
        return base

    def setTopicArgs(self):
        pass

    def setCode(self, code):
        pass