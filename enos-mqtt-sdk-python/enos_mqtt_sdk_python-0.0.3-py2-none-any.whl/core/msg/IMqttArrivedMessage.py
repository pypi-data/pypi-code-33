from abc import ABCMeta, abstractmethod
from IMqttMessage import IMqttMessage
import json
from core.exception.EnvisionException import EnvisionException


class IMqttArrivedMessage(IMqttMessage):
    __metaclass__ = ABCMeta

    def getMatchTopicPattern(self):
        pass

    def decodeToObject(self, msg):
        pass

    def getClass(self):
        pass

    def match(self, topic):
        return self.getMatchTopicPattern().findall(topic)

    def decode(self, topic, payload):
        path = self.match(topic)
        if path is None or len(path) <= 0:
            return None
        arrivedMsg = None
        arrivedObj = None
        try:
            arrivedMsg = json.loads(payload)
            arrivedObj = self.decodeToObject(arrivedMsg)
        except:
            raise EnvisionException('load json error')

        arrivedObj.setMessageTopic(topic)
        if len(path) > 0 and len(path[0]) > 0:
            arrivedObj.setProductKey(path[0][0])

        if len(path) > 0 and len(path[0]) > 1:
            arrivedObj.setDeviceKey(path[0][1])

        return DecodeResult(arrivedObj, path)


class DecodeResult(object):

    def __init__(self, arrivedMsg, pathValueList):
        self.arrivedMsg = arrivedMsg
        self.pathList = pathValueList

    def getPathList(self):
        return self.pathList

    def getTopicPath(self, index):
        return self.pathList[index]

    def getArrivedMsg(self):
        return self.arrivedMsg