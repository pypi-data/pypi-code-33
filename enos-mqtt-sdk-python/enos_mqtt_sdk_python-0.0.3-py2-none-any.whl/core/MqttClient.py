from core.profile.Profile import Profile
from core.internals.MqttConnection import MqttConnection
from core.msg.IMessageHandler import IMessageHandler
from atomic import AtomicLong
from functools import partial
import logging
import logging.config
import os
import json


class MqttClient(object):

    _logger = logging.getLogger(__name__)
    requestId = AtomicLong(0)

    def __init__(self, uri, productKey, deviceKey, deviceSecret, profile=None):
        if profile is not None:
            self.profile = profile
        else:
            self.profile = Profile(uri, productKey, deviceKey, deviceSecret)
        self.connection = MqttConnection(self.profile)
        self.messageHandler = IMessageHandler()

    def loadCallback(self):
        self.connection.onOnline = self.onOnline
        self.connection.onOffline = self.onOffline

    def setupBasicLogger(self, level='INFO', filePath=None, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'):
        if filePath is not None:
            logging.basicConfig(level=level, filename=filePath, format=format)
        else:
            logging.basicConfig(level=level, format=format)

    def setupFileLogger(self, filePath):
        path = filePath
        if os.path.exists(path):
            with open(path, "r") as f:
                config = json.load(f)
                logging.config.dictConfig(config)

    def onOnline(self):
        pass

    def onOffline(self):
        pass

    def getProfile(self):
        return self.profile

    def fastPublish(self, request):
        try:
            self.fillRequest(request)
            request.check()
            self.connection.fastPublish(request)
        except Exception as e:
            self._logger.error('fastPublish failed: %s' % e.message)

    def publish(self, request, callback=None):
        try:
            self.fillRequest(request)
            request.check()
            return self.connection.publish(request, callback)
        except Exception as e:
            self._logger.error('publish failed: %s' % e.message)

    def setArrivedMsgHandler(self, arrivedMsgCls, handler):
        self.connection.getProcessor().setArrivedMsgHandler(arrivedMsgCls, handler)

    def connect(self, callback = None):
        try:
            self.loadCallback()
            self.connection.connect(callback)
        except Exception as e:
            self._logger.error('connect faild: %s' % e.message)

    def disconnect(self, callback = None):
        try:
            self.connection.disconnect(callback)
        except Exception as e:
            self._logger.error('disconnect failed: %s' % e.message)

    def close(self):
        self.connection.close()

    def isConnected(self):
        return self.connection.isConnected()

    def fillRequest(self, request):
        if request.getMessageId() is None or request.getMessageId() == '':
            request.setMessageId(str(self.requestId.value))

        if request.getVersion() is None or request.getVersion() == '':
            request.setVersion(self.profile.VERSION)

        if ((request.getProductKey() is None or request.getProductKey() == '')
            and (request.getDeviceKey() is None or request.getDeviceKey() == '')):
            request.setProductKey(self.profile.getProductKey())
            request.setDeviceKey(self.profile.getDeviceKey())

    def onMessage(self, msgHandler):
        self.setArrivedMsgHandler('MeasurepointSetCommand', self.messageHandler)
        self.messageHandler.onMessage = partial(self.messageHandler.onMessage, msgHandler=msgHandler)