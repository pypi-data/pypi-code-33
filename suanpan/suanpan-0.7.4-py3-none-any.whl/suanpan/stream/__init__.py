# coding=utf-8
from __future__ import print_function

import argparse
import contextlib
import itertools
import json
import time
import traceback
import uuid

from suanpan import objects, interfaces
from suanpan.arguments import Bool, Int, String
from suanpan.components import Component
from suanpan.dw import dw
from suanpan.storage import storage
from suanpan.log import logger
from suanpan.mq import mq
from suanpan.mstorage import mstorage


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
        outputs = None
        if results is not None:
            outputs = self.saveOutputs(context, results)
            outputs = self.formatAsOuts(outputs)
            outputs = self.stringifyOuts(outputs)
        self.closeContext()
        return outputs

    @contextlib.contextmanager
    def context(self, message):
        yield objects.Context(message=message)

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


class Stream(interfaces.HasLogger, interfaces.HasBaseServices):

    defaultStreamCall = "call"
    streamArguments = [
        String("stream-node-id", required=True),
        String("stream-node-group", default="default"),
        String("stream-recv-queue", required=True),
        String("stream-send-queue", required=True),
    ]
    defaultArguments = list(
        itertools.chain(
            streamArguments,
            mq.ARGUMENTS,
            mstorage.ARGUMENTS,
            dw.ARGUMENTS,
            storage.ARGUMENTS,
        )
    )
    arguments = []

    def __init__(self):
        super(Stream, self).__init__()
        self.args = self.parseArgs()
        self.transformArguments(objects.Context(), self.args)
        self.setOptions(self.args)
        self.setBaseServices(self.args)
        self.afterInit()

    def generateRequestId(self):
        return uuid.uuid4().hex

    def formatMessage(self, message, msg, costTime=None):
        msgs = [message["id"], message.get("type", self.defaultStreamCall), msg]
        if costTime is not None:
            msgs.insert(-1, "{}s".format(costTime))
        return " - ".join(msgs)

    def streamCall(self, message):
        logger.info(self.formatMessage(message, msg="Start"))
        startTime = time.time()
        try:
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
        streamCall = message.get("type", self.defaultStreamCall)
        callFunction = getattr(self, streamCall, None)
        if not callFunction:
            raise Exception("Unknown stream call: {}.{}".format(self.name, streamCall))
        return callFunction

    def call(self, message, *args):
        raise NotImplementedError("Method not implemented!")

    def start(self):
        for message in self.subscribe():
            message = self.setDefaultMessageType(message)
            self.streamCall(message["data"])

    def setDefaultMessageType(self, message):
        message["data"].setdefault("type", self.defaultStreamCall)
        return message

    def setOptions(self, args):
        self.options = self.defaultArgumentsFormat(args, self.streamArguments)
        return self.options

    def getArguments(self):
        return itertools.chain(self.defaultArguments, self.arguments)

    def transformArguments(self, context, args):
        self.loadArguments(args, self.arguments)
        self.formatArguments(context, self.arguments)
        for arg in self.arguments:
            setattr(self.args, arg.key, arg.value)
        return self.args

    def afterInit(self):
        pass

    def createQueues(self, force=False):
        mq.createQueue(self.options["recvQueue"], force=force)
        mq.createQueue(self.options["sendQueue"], force=force)

    def subscribe(self, **kwargs):
        yield from mq.subscribeQueue(
            self.options["recvQueue"],
            group=self.options["nodeGroup"],
            consumer=self.options["nodeId"],
            **kwargs
        )

    def recv(self, **kwargs):
        return mq.recvMessages(
            self.options["recvQueue"],
            group=self.options["nodeId"],
            consumer=self.name,
            **kwargs
        )

    def send(self, message, data, queue=None):
        queue = queue or self.options["sendQueue"]
        data = {
            "node_id": self.options["nodeId"],
            "request_id": message["id"],
            "type": message.get("type", self.defaultStreamCall),
            **data,
        }
        logger.debug("Send to `{}`: {}".format(queue, data))
        return mq.sendMessage(queue, data)

    def sendSuccessMessage(self, message, data, queue=None):
        keys = ["out{}".format(i + 1) for i in range(5)]
        if not self.keysAllIn(data.keys(), keys):
            raise Exception("Success Message data only accept keys: {}".format(keys))
        data = {key: data.get(key) for key in keys if data.get(key) is not None}
        return self.send(message, data, queue=queue)

    def sendFailureMessage(self, message, msg, queue=None):
        if not isinstance(msg, str):
            raise Exception("Failure Message msg only accept string")
        return self.send(message, {"msg": msg}, queue=queue)

    def sendMissionMessage(self, message, data, queue=None):
        keys = ["in{}".format(i + 1) for i in range(5)] + ["extra"]
        if not self.keysAllIn(data.keys(), keys):
            raise Exception("Mission Message data only accept keys: {}".format(keys))
        return self.send(message, data, queue=queue)

    def keysAllIn(self, keys, kset):
        return len(set(keys) - set(kset)) == 0

    def get(self, key):
        return mstorage.get(key)

    def set(self, key, value, **kwargs):
        return mstorage.set(key, value, **kwargs)

    def delete(self, key):
        return mstorage.delete(key)
