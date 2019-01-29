from message.upstream.BaseMqttResponse import BaseMqttResponse
from core.internals.constants.ArrivedTopicPattern import ArrivedTopicPattern
import re


class TopoGetResponse(BaseMqttResponse):

    def getMatchTopicPattern(self):
        return re.compile(ArrivedTopicPattern.TOPO_GET_REPLY)

    def decodeToObject(self, msg):
        base = TopoGetResponse()
        base.__dict__ = msg
        return base

    def getClass(self):
        return 'TopoGetResponse'