from message.upstream.BaseMqttResponse import BaseMqttResponse
from core.internals.constants.ArrivedTopicPattern import ArrivedTopicPattern
import re


class MeasurepointPostResponse(BaseMqttResponse):

   def getMatchTopicPattern(self):
       return re.compile(ArrivedTopicPattern.MEASUREPOINT_POST_REPLY)

   def decodeToObject(self, msg):
       base = MeasurepointPostResponse()
       base.__dict__ = msg
       return base

   def getClass(self):
       return 'MeasurepointPostResponse'