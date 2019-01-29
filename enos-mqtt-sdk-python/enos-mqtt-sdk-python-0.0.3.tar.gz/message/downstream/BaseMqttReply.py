from core.msg.IMqttReply import IMqttReply
from message.BaseAckMessage import BaseAckMessage
from core.internals.constants.DeliveryTopicFormat import DeliveryTopicFormat


class BaseMqttReply(BaseAckMessage, IMqttReply):

    def __init__(self):
        super(BaseMqttReply, self).__init__()
        self.productKey = ''
        self.deviceKey = ''
        self.messageTopic = ''
        self.qos = 1

    def getQos(self):
        return self.qos

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
        base = BaseMqttReply()
        base.__dict__ = msg
        return base

    def _getPK_DK_FormatTopic(self):
        return DeliveryTopicFormat.MEASUREPOINT_SET_REPLY

    def setTopicArgs(self):
        messageTopic = self._getPK_DK_FormatTopic().format(self.productKey, self.deviceKey)
        self.setMessageTopic(messageTopic)

    def getAnswerTopic(self):
        return self.getMessageTopic() + '_reply'

    def reply_with_payload(self, code, message, data):
        self.setCode(code)
        self.setMessage(message)
        self.setData(data)