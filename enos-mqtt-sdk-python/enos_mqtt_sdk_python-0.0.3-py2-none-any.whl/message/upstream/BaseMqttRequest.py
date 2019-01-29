from abc import ABCMeta
from core.msg.IMqttRequest import IMqttRequest
from message.BaseAnswerableMessage import BaseAnswerableMessage
from util.CheckUtil import CheckUtil
from core.exception.EnvisionException import EnvisionException


class BaseMqttRequest(BaseAnswerableMessage, IMqttRequest):
    __metaclass__ = ABCMeta

    def __init__(self):
        super(BaseMqttRequest, self).__init__()
        self.qos = 1
        self.productKey = ''
        self.deviceKey = ''

    def getResponse(self):
        pass

    def getProductKey(self):
        return self.productKey

    def setProductKey(self, productKey):
        self.productKey = productKey

    def getDeviceKey(self):
        return self.deviceKey

    def setDeviceKey(self, deviceKey):
        self.deviceKey = deviceKey

    def getMessageId(self):
        return self.getId()

    def setMessageId(self, msgId):
        self.setId(msgId)

    def check(self):
        CheckUtil.checkNotEmpty(self.getProductKey(), 'productKey is none')
        CheckUtil.checkNotEmpty(self.getDeviceKey(), 'deviceKey is none')

    def getQos(self):
        return self.qos

    def setQos(self, qos):
        if qos<0 or qos >=2:
            raise EnvisionException('qos only suport 0,1 in current version')
        self.qos = qos

    def _getPK_DK_FormatTopic(self):
        pass

    def getMessageTopic(self):
        return self._getPK_DK_FormatTopic().format(self.getProductKey(), self.getDeviceKey())

    def getAnswerTopic(self):
        return self.getMessageTopic() + '_reply'

    def setTopicArgs(self):
        pass


class Builder(object):
    __metaclass__ = ABCMeta

    def createMethod(self):
        return ''

    def createParams(self):
        return ''

    def createRequestInstance(self):
        pass

    def __init__(self):
        self.productKey = ''
        self.deviceKey = ''

    def setProductKey(self, productKey):
        self.productKey = productKey
        return self

    def setDeviceKey(self, deviceKey):
        self.deviceKey = deviceKey
        return self

    def build(self):
        request = self.createRequestInstance()
        if (self.productKey != ''):
            request.productKey = self.productKey

        if (self.deviceKey != ''):
            request.deviceKey = self.deviceKey

        request.method = self.createMethod()
        request.params = self.createParams()
        return request