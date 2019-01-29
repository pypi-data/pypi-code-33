from message.downstream.BaseMqttCommand import BaseMqttCommand
from core.internals.constants.ArrivedTopicPattern import ArrivedTopicPattern

import re


class MeasurepointSetCommand(BaseMqttCommand):

   def getMatchTopicPattern(self):
       return re.compile(ArrivedTopicPattern.MEASUREPOINT_SET_COMMAND)

   def decodeToObject(self, msg):
       base = MeasurepointSetCommand()
       base.__dict__ = msg
       return base

   def getClass(self):
       return 'MeasurepointSetCommand'