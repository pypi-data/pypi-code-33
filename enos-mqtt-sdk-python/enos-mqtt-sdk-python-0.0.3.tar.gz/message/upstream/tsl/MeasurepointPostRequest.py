from message.upstream.BaseMqttRequest import BaseMqttRequest
from message.upstream.BaseMqttRequest import Builder
from core.internals.constants.MethodConstants import MethodConstants
from core.internals.constants.DeliveryTopicFormat import DeliveryTopicFormat
import time
from message.upstream.tsl.MeasurepointPostResponse import MeasurepointPostResponse


class MeasurepointPostRequest(BaseMqttRequest):

    @classmethod
    def builder(cls):
        return Builder()

    def check(self):
        super(MeasurepointPostRequest, self).check()

    def _getPK_DK_FormatTopic(self):
        return DeliveryTopicFormat.MEASUREPOINT_POST

    def getAnswerType(self):
        return MeasurepointPostResponse()

    def getResponse(self):
        return MeasurepointPostResponse()



class Builder(Builder):

    def __init__(self):
        super(Builder, self).__init__()
        self.params = dict()
        self.params['measurepoints'] = dict()
        self.params['time'] = int(time.time()*1000)

    def addMeasurePoint(self, key, value):
        self.params['measurepoints'][key] = value
        return self

    def addMeasurePoints(self, values):
        for value in values:
            self.params['measurepoints'][value] = values[value]
        return self

    def setMeasurePoints(self, value):
        self.params['measurepoints'] = value
        return self

    def setTimestamp(self, timestamp):
        self.params['time'] = timestamp
        return self

    def createMethod(self):
        return MethodConstants.MEASUREPOINT_POST

    def createParams(self):
        return self.params

    def createRequestInstance(self):
        return MeasurepointPostRequest()