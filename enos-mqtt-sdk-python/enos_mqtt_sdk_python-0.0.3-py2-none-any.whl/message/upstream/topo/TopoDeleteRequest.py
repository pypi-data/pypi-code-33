from message.upstream.BaseMqttRequest import BaseMqttRequest
from message.upstream.BaseMqttRequest import Builder
from message.upstream.topo.TopoDeleteResponse import TopoDeleteResponse
from util.CheckUtil import CheckUtil
from core.internals.constants.MethodConstants import MethodConstants
from core.internals.constants.DeliveryTopicFormat import DeliveryTopicFormat


class TopoDeleteRequest(BaseMqttRequest):

    @classmethod
    def builder(cls):
        return Builder()

    def _getPK_DK_FormatTopic(self):
        return DeliveryTopicFormat.TOPO_DELETE_TOPIC_FMT

    def getAnswerType(self):
        return TopoDeleteResponse()

    def getResponse(self):
        return TopoDeleteResponse()


class Builder(Builder):

    def __init__(self):
        super(Builder, self).__init__()
        self.subDeviceList = list()

    def setSubDevices(self, subDeviceList):
        self.subDeviceList = subDeviceList
        return self

    def setSubDeviceList(self, subDeviceList):
        self.subDeviceList = subDeviceList
        return self

    def addSubDevice(self, productKey, deviceKey):
        self.subDeviceList.append((productKey, deviceKey))
        return self

    def addSubDevices(self, subDeviceList):
        for subDevice in subDeviceList:
            self.subDeviceList.append(subDevice)
        return self

    def addSubDeviceList(self, subDeviceList):
        for subDeivce in subDeviceList:
            self.subDeviceList.append(subDeivce)
        return self

    def createMethod(self):
        return MethodConstants.TOPO_DELETE

    def createParams(self):
        params = list()
        for subDevice in self.subDeviceList:
            if len(subDevice) >= 2:
                subDeviceDict = dict()
                subDeviceDict['productKey'] = subDevice[0]
                subDeviceDict['deviceKey'] =  subDevice[1]
                params.append(subDeviceDict)
        return params

    def createRequestInstance(self):
        return TopoDeleteRequest()