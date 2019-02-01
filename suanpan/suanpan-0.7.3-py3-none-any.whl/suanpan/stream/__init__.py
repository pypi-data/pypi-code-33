# coding=utf-8
from __future__ import print_function

import argparse
import contextlib
import itertools
import json
import tempfile
import time
import traceback
import uuid

from suanpan import Context
from suanpan.arguments import Bool, Int, String
from suanpan.components import Component
from suanpan.datawarehouse import dw
from suanpan.io import storage
from suanpan.log import logger
from suanpan.mq import mq


class Handler(Component):
    def __call__(self, steamObj, message, *arg, **kwargs):
        return self.run(steamObj, message, *arg, **kwargs)

    def run(self, steamObj, message, *arg, **kwargs):
        handlerContext = self.init(message)
        results = self.runFunc(steamObj, handlerContext)
        return self.save(handlerContext, results)

    def init(self, message):
        restArgs = self.getArgList(message)
        handlerContext = self.getContext(message)
        args, restArgs = self.parseArguments(self.getArguments(), restArgs)
        args = self.transformArguments(handlerContext, args)
        setattr(handlerContext, "args", args)
        return handlerContext

    def save(self, context, results):
        outputs = self.saveOutputs(context, results)
        outputs = self.formatAsOuts(outputs)
        outputs = self.stringifyOuts(outputs)
        self.closeContext()
        return outputs

    @contextlib.contextmanager
    def context(self, message):
        yield Context(message=message)

    def getArgList(self, message):
        inputArguments = itertools.chain(
            *[
                ["--{}".format(arg.key), message.get("in{}".format(i + 1))]
                for i, arg in enumerate(self.getArguments("inputs"))
                if message.get("in{}".format(i + 1)) is not None
            ]
        )

        extra = json.loads(message.get("extra", {}))
        output = extra.get("output", {})
        outputArguments = itertools.chain(
            *[
                [
                    "--{}".format(arg.key),
                    self.getOutputTmpValue(message, output.get("out{}".format(i + 1))),
                ]
                for i, arg in enumerate(self.getArguments("outputs"))
                if output.get("out{}".format(i + 1)) is not None
            ]
        )
        return list(itertools.chain(inputArguments, outputArguments))

    def formatAsOuts(self, results):
        return {
            "out{}".format(i + 1): results[arg.key]
            for i, arg in enumerate(self.getArguments("outputs"))
            if results[arg.key] is not None
        }

    def stringifyOuts(self, outs):
        return {k: str(v) for k, v in outs.items()}

    def shortenRequestID(self, requestID):
        return requestID.replace("-", "")

    def getOutputTmpValue(self, message, output):
        shortRequestID = self.shortenRequestID(message["id"])
        return (
            storage.pathJoin(output, shortRequestID)
            if self.isStoragePath(output)
            else "{}_{}".format(output, shortRequestID)
        )

    def isStoragePath(self, value):
        return storage.delimiter in value


class Stream(object):

    defaultStreamCall = "call"
    mqArguments = [
        String("mq-type", default="redis"),
        String("mq-redis-name"),
        String("mq-redis-host", default="localhost"),
        Int("mq-redis-port", default=6379),
        Bool("mq-redis-realtime", default=False),
        String("mq-redis-recv-queue", default="mission"),
        String("mq-redis-send-queue", default="master"),
        String("mq-redis-group", default="default"),
    ]
    dataWarehouseArguments = [
        String("dw-type", default="hive"),
        String("dw-hive-host", default="localhost"),
        Int("dw-hive-port"),
        String("dw-hive-database", default="default"),
        String("dw-hive-username"),
        String("dw-hive-password"),
        String("dw-hive-auth"),
        String("dw-odps-access-id"),
        String("dw-odps-access-key"),
        String(
            "dw-odps-endpoint", default="http://service.cn.maxcompute.aliyun.com/api"
        ),
        String("dw-odps-project"),
    ]
    storageArguments = [
        String("storage-type", default="oss"),
        String("storage-oss-access-id"),
        String("storage-oss-access-key"),
        String("storage-oss-bucket-name", default="suanpan"),
        String("storage-oss-endpoint", default="http://oss-cn-beijing.aliyuncs.com"),
        String("storage-oss-delimiter", default="/"),
        String("storage-oss-temp-store", default=tempfile.gettempdir()),
        Int("storage-oss-download-num-threads", default=1),
        String("storage-oss-download-store-name", default=".py-oss-download"),
        Int("storage-oss-upload-num-threads", default=1),
        String("storage-oss-upload-store-name", default=".py-oss-upload"),
    ]
    defaultArguments = mqArguments + dataWarehouseArguments + storageArguments
    arguments = []

    def __init__(self):
        logger.setLogger(self.name)
        self.args = self.parseArgs()
        self.transformArguments(Context(), self.args)
        self.setMQ(self.args)
        self.setDataWarehouse(self.args)
        self.setStorage(self.args)
        self.afterInit()

    @property
    def name(self):
        return self.__class__.__name__

    def generateRequestId(self):
        return uuid.uuid4().hex

    def formatMessage(self, message, msg, costTime=None):
        msgs = [message["id"], message.get("type") or self.defaultStreamCall, msg]
        if costTime is not None:
            msgs.insert(-1, "{}s".format(costTime))
        return " - ".join(msgs)

    def predict(self, message):
        try:
            logger.info(self.formatMessage(message, msg="Start"))
            startTime = time.time()
            callFunction = self.getCallFunction(message)
            outputs = callFunction(self, message) or {}
            endTime = time.time()
            costTime = round(endTime - startTime, 3)
            logger.info(self.formatMessage(message, msg="Done", costTime=costTime))
            if outputs:
                self.sendSuccessMessage(message, outputs)
        except:
            tracebackInfo = traceback.format_exc()
            endTime = time.time()
            costTime = round(endTime - startTime, 3)
            logger.error(
                self.formatMessage(message, msg=tracebackInfo, costTime=costTime)
            )
            self.sendFailureMessage(message, tracebackInfo)

    def getCallFunction(self, message):
        streamCall = message.get("type") or self.defaultStreamCall
        callFunction = getattr(self, streamCall, None)
        if not callFunction:
            raise Exception("Unknown stream call: {}.{}".format(self.name, streamCall))
        return callFunction

    def call(self, message, *args):
        raise NotImplementedError("Method not implemented!")

    def start(self):
        for message in mq.subscribe():
            self.predict(message["data"])

    def setMQ(self, args):
        return mq.setBackend(**self.defaultArgumentsFormat(args, self.mqArguments))

    def setDataWarehouse(self, args):
        return dw.setBackend(
            **self.defaultArgumentsFormat(args, self.dataWarehouseArguments)
        )

    def setStorage(self, args):
        return storage.setBackend(
            **self.defaultArgumentsFormat(args, self.storageArguments)
        )

    def getArguments(self):
        return itertools.chain(self.defaultArguments, self.arguments)

    def parseArgs(self):
        return self.parseArguments(self.getArguments())

    def parseArguments(self, arguments, *args, **kwargs):
        parser = argparse.ArgumentParser(*args, **kwargs)
        for arg in arguments:
            arg.addParserArguments(parser)
        return parser.parse_known_args()[0]

    def transformArguments(self, context, args):
        self.loadArguments(args, self.arguments)
        self.formatArguments(context, self.arguments)
        for arg in self.arguments:
            setattr(self.args, arg.key, arg.value)
        return self.args

    def loadArguments(self, args, arguments):
        return {arg.key: arg.load(args) for arg in arguments}

    def formatArguments(self, context, arguments):
        return {arg.key: arg.format(context) for arg in arguments}

    def defaultArgumentsFormat(self, args, arguments):
        arguments = (arg.key.replace("-", "_") for arg in arguments)
        return {
            self.defaultArgumentKeyFormat(arg): getattr(args, arg) for arg in arguments
        }

    def defaultArgumentKeyFormat(self, key):
        return self.toCamelCase(self.removePrefix(key))

    def removePrefix(self, string, delimiter="_", num=1):
        pieces = string.split(delimiter)
        pieces = pieces[num:] if len(pieces) > num else pieces
        return delimiter.join(pieces)

    def toCamelCase(self, string, delimiter="_"):
        camelCaseUpper = lambda i, s: s[0].upper() + s[1:] if i and s else s
        return "".join(
            [camelCaseUpper(i, s) for i, s in enumerate(string.split(delimiter))]
        )

    def afterInit(self):
        pass

    def send(self, message, data):
        return mq.send({"request_id": message["id"], **data})

    def sendSuccessMessage(self, message, data):
        keys = ("out{}".format(i + 1) for i in range(5))
        data = {key: data.get(key) for key in keys if data.get(key) is not None}
        return mq.sendSuccessMessage({"request_id": message["id"], **data})

    def sendFailureMessage(self, message, msg):
        return mq.sendFailureMessage({"request_id": message["id"], "msg": msg})
