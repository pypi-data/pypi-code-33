from message.upstream.BaseMqttRequest import BaseMqttRequest
from message.upstream.BaseMqttRequest import Builder
from message.upstream.status.SubDeviceLoginInfo import SubDeviceLoginInfo
from core.internals.constants.DeliveryTopicFormat import DeliveryTopicFormat
from message.upstream.status.SubDeviceLoginResponse import SubDeviceLoginResponse
from core.internals.constants.MethodConstants import MethodConstants
from util.CheckUtil import CheckUtil


class SubDeviceLoginRequest(BaseMqttRequest):

    @classmethod
    def builder(cls):
        return Builder()

    def check(self):
        super(SubDeviceLoginRequest, self).check()
        params = self.getParams()
        CheckUtil.checkNotEmpty(params['productKey'], 'subDeviceInfo.productKey')
        CheckUtil.checkNotEmpty(params['deviceKey'], 'subDeviceInfo.deviceKey')
        CheckUtil.checkNotEmpty(params['clientId'], 'subDeviceInfo.client')
        CheckUtil.checkNotEmpty(params['signMethod'], 'subDeviceInfo.signMethod')
        CheckUtil.checkNotEmpty(params['sign'], 'subDeviceInfo.sign')

    def _getPK_DK_FormatTopic(self):
        return DeliveryTopicFormat.SUB_DEVICE_LOGIN_TOPIC_FMT

    def getAnswerType(self):
        return SubDeviceLoginResponse()

    def getResponse(self):
        return SubDeviceLoginResponse()

class Builder(Builder):

    def setSubDeviceInfo(self, productKey, deviceKey, deviceSecret):
        self.subDeviceInfo = SubDeviceLoginInfo(productKey, deviceKey, deviceSecret)
        return self

    def createMethod(self):
        return MethodConstants.SUB_DEVICE_LOGIN

    def createParams(self):
        return self.subDeviceInfo.getSignParams()

    def createRequestInstance(self):
        return SubDeviceLoginRequest()