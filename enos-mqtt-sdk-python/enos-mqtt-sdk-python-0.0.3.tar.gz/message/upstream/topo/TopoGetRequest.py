from message.upstream.BaseMqttRequest import BaseMqttRequest
from message.upstream.BaseMqttRequest import Builder
from core.internals.constants.MethodConstants import MethodConstants
from core.internals.constants.DeliveryTopicFormat import DeliveryTopicFormat
from message.upstream.topo.TopoGetResponse import TopoGetResponse


class TopoGetRequest(BaseMqttRequest):

    @classmethod
    def builder(cls):
        return Builder()

    def getAnswerType(self):
        return TopoGetResponse()

    def getResponse(self):
        return TopoGetResponse()

    def _getPK_DK_FormatTopic(self):
        return DeliveryTopicFormat.TOPO_GET_TOPIC_FMT


class Builder(Builder):

    def createMethod(self):
        return MethodConstants.TOPO_GET

    def createParams(self):
        return dict()

    def createRequestInstance(self):
        return TopoGetRequest()