from message.upstream.BaseMqttRequest import BaseMqttRequest
from message.upstream.BaseMqttRequest import Builder
from core.internals.constants.MethodConstants import MethodConstants
from core.internals.constants.DeliveryTopicFormat import DeliveryTopicFormat
from message.upstream.topo.TopoAddResponse import TopoAddResponse
from util.CheckUtil import CheckUtil


class TopoAddRequest(BaseMqttRequest):

    @classmethod
    def builder(cls):
        return Builder()

    def check(self):
        super(TopoAddRequest, self).check()
        params = self.getParams()
        for param in params:
            CheckUtil.checkNotEmpty(param['productKey'], 'subDeviceInfo.productKey')
            CheckUtil.checkNotEmpty(param['deviceKey'], 'subDeviceInfo.deviceKey')
            CheckUtil.checkNotEmpty(param['clientId'], 'subDeviceInfo.clientId')
            CheckUtil.checkNotEmpty(param['signMethod'], 'subDeviceInfo.signMethod')
            CheckUtil.checkNotEmpty(param['sign'], 'subDeviceInfo.sign')

    def _getPK_DK_FormatTopic(self):
        return DeliveryTopicFormat.TOPO_ADD_TOPIC_FMT

    def getAnswerType(self):
        return TopoAddResponse()

    def getResponse(self):
        return TopoAddResponse()


class Builder(Builder):

    def __init__(self):
        super(Builder, self).__init__()
        self.subDeviceInfoList = list()

    def setSubDeviceInfoList(self, subDeviceInfoList):
        self.subDeviceInfoList = subDeviceInfoList
        return self

    def addSubDevice(self, deviceInfo):
        self.subDeviceInfoList.append(deviceInfo)
        return self

    def addSubDevices(self, deviceInfos):
        self.subDeviceInfoList.extend(deviceInfos)
        return self

    def createMethod(self):
        return MethodConstants.TOPO_ADD

    def createParams(self):
        params = list()
        for deviceInfo in self.subDeviceInfoList:
            params.append(deviceInfo.createSignMap())
        return params

    def createRequestInstance(self):
        return TopoAddRequest()