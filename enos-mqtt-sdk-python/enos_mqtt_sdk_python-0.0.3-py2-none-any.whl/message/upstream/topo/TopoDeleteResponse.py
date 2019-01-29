from message.upstream.BaseMqttResponse import BaseMqttResponse
from core.internals.constants.ArrivedTopicPattern import ArrivedTopicPattern
import re


class TopoDeleteResponse(BaseMqttResponse):

    def getMatchTopicPattern(self):
        return re.compile(ArrivedTopicPattern.TOPO_DELETE_REPLY)

    def decodeToObject(self, msg):
        base = TopoDeleteResponse()
        base.__dict__ = msg
        return base

    def getClass(self):
        return 'TopoDeleteResponse'