import time
from core.msg.IMqttResponse import IMqttResponse
from core.msg.IMessageHandler import IMessageHandler
from message.downstream.BaseMqttReply import BaseMqttReply
from core.internals.DecoderRegistry import DecoderRegistry
from core.exception.EnvisionException import EnvisionException
import logging


class DefaultProcessor(object):

    _logger = logging.getLogger(__name__)

    def __init__(self, mqttClient, profile, subTopicCache):
        self.mqttClient = mqttClient
        self.executor = None
        self.subTopicCache = subTopicCache
        self.connectCallback = None
        self.disconnectCallback = None
        self.rspTaskMap = dict()
        self.executor = profile.getExecutor()
        self.profile = profile
        self.arrivedMsgHandlerMap = dict()

    def setConnectCallback(self, connectCallback):
        self.connectCallback = connectCallback

    def setDisconnectCallback(self, disconnectCallback):
        self.disconnectCallback = disconnectCallback

    def onConnected(self):
        if self.connectCallback is not None:
            self.connectCallback

    def onConnectFailed(self):
        if self.disconnectCallback is not None:
            self.disconnectCallback

    def setArrivedMsgHandler(self, arrivedMsgCls, handler):
        self.arrivedMsgHandlerMap[arrivedMsgCls] = handler

    def messageArrived(self, message):
        try:
            result = DecoderRegistry.getDecode(message)
            if result is None:
                raise EnvisionException('decode the rcv message failed')
            msg = result.getArrivedMsg()
            if msg is None:
                raise EnvisionException('decode msg failed')
            if isinstance(msg, IMqttResponse):
                key = message.topic + '_' + msg.getMessageId()
                task = self.rspTaskMap.pop(key)
                if task is None:
                    return
                task.run(msg)
                #self.executor.submit(task.runable)
            else:
                handler = self.arrivedMsgHandlerMap.get(msg.getClass())
                handler = handler if handler is not None else IMessageHandler()
                pathList = result.getPathList()
                # if handler is not None:
                # self.messageHandler(msg, handler, pathList)
                self.executor.submit(self.messageHandler, msg, handler, pathList)

        except Exception as e:
            self._logger.error('message decode failed: %s' % e.message)

    def messageHandler(self, msg, handler, pathList):
        try:
            deliveryMsg = handler.onMessage(msg, pathList)
            if deliveryMsg is not None:
                deliveryMsg.setMessageId(msg.getMessageId())
                deliveryMsg.setProductKey(msg.getProductKey())
                deliveryMsg.setDeviceKey(msg.getDeviceKey())
                if isinstance(deliveryMsg, BaseMqttReply):
                    deliveryMsg.setTopicArgs()
                    self.mqttClient.publish_async(deliveryMsg.getMessageTopic(), deliveryMsg.encode(),
                                                  deliveryMsg.getQos(), False)
        except Exception as e:
            raise EnvisionException(e.message)

    def doFastPublish(self, request):
        try:
            request.check()
            self.mqttClient.publish_async(request.getMessageTopic(),request.encode(),request.getQos(), False)
        except Exception as e:
            raise EnvisionException(e.message)

    def createCallbackTask(self, request, callback, timeout):
        if callback is not None:
            task = Task(timeout)
            key = request.getAnswerTopic() + '_' + request.getMessageId()
            isTimeOut = False
            futureTask = self.executor.submit(self.delayTask(timeout, self.futureTask1(key, isTimeOut)))
            task.setRunnable(self.futureTask2(task, futureTask, callback))
            self.rspTaskMap[key] = task
        self.doFastPublish(request)

    def createFutureTask(self, request):
        key = request.getAnswerTopic() + '_' + request.getMessageId()
        task = Task(self.profile.getTimeToWait())
        futureTask = self.executor.submit(task.call)
        task.setRunable(futureTask)
        self.rspTaskMap[key] = task
        self.doFastPublish(request)
        return futureTask

    def delayTask(self, timeout, back):
        time.sleep(timeout)
        return back

    def futureTask1(self, key, result):
        self.rspTaskMap.pop(key)
        return result

    def futureTask2(self, task, futureTask, callback):
        callback.onResponse(task.rsp)
        if not futureTask.done():
            futureTask.cancle()


class Task(object):

    def __init__(self, timeout=60):
        self.rsp = None
        self.runable = None
        self.timeout = timeout

    def setRunable(self, runable):
        self.runable = runable

    def run(self, rsp):
        self.rsp = rsp

    def call(self):
        sleep_time = 0
        while True:
            if self.rsp is not None or sleep_time >= self.timeout:
                return self.rsp
            time.sleep(1)
            sleep_time+=1