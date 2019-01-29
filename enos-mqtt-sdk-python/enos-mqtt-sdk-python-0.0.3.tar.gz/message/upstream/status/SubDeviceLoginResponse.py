from message.upstream.BaseMqttResponse import BaseMqttResponse
from core.internals.constants.ArrivedTopicPattern import ArrivedTopicPattern
import re

class SubDeviceLoginResponse(BaseMqttResponse):

    def getSubProductKey(self):
        data = self.getData()
        return data['productKey']

    def getSubDeviceKey(self):
        data = self.getData()
        return data['deviceKey']

    def getMatchTopicPattern(self):
        return re.compile(ArrivedTopicPattern.SUB_DEVICE_LOGIN_REPLY)

    def decodeToObject(self, msg):
        base = SubDeviceLoginResponse()
        base.__dict__ = msg
        return base

    def getClass(self):
        return 'SubDeviceLoginResponse'
