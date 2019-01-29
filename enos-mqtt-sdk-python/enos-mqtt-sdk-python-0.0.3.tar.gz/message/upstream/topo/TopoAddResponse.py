from message.upstream.BaseMqttResponse import BaseMqttResponse
from core.internals.constants.ArrivedTopicPattern import ArrivedTopicPattern
import re


class TopoAddResponse(BaseMqttResponse):

    def getMatchTopicPattern(self):
        return re.compile(ArrivedTopicPattern.TOPO_ADD_REPLY)

    def decodeToObject(self, msg):
        base = TopoAddResponse()
        base.__dict__ = msg
        return base

    def getClass(self):
        return 'TopoAddResponse'
