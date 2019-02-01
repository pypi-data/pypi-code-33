# coding=utf-8
from __future__ import print_function

import time
import traceback

import redis


class RedisMQ(object):
    def __init__(
        self,
        redisName,
        redisHost="localhost",
        redisPort=6379,
        redisRealtime=False,
        redisRecvQueue="mission",
        redisSendQueue="master",
        redisGroup="default",
        options=None,
        client=None,
        **kwargs
    ):
        self.name = redisName
        self.options = options or {}
        self.options.update(
            name=self.name,
            host=redisHost,
            port=redisPort,
            realtime=redisRealtime,
            recvQueue=redisRecvQueue,
            sendQueue=redisSendQueue,
            group=redisGroup,
        )
        self.client = RedisMQClient(
            host=self.options["host"],
            port=self.options["port"],
            client=client,
            realtime=self.options["realtime"],
        )
        self.kvclient = self.client.client

    def createQueues(self, force=False):
        self.createQueue(self.options["recvQueue"], force=force)
        self.createQueue(self.options["sendQueue"], force=force)

    def createQueue(self, name, group="default", consumeID="0", force=False):
        if force:
            self.client.deleteQueue(name)
        return self.client.createQueue(name, group=group, consumeID=consumeID)

    def subscribe(
        self,
        noack=False,
        block=True,
        count=1,
        consumeID=">",
        delay=1,
        errDelay=1,
        errCallback=print,
    ):
        yield from self.client.subscribeQueue(
            self.options["recvQueue"],
            group=self.options["group"],
            consumer=self.name,
            noack=noack,
            block=block,
            count=count,
            consumeID=consumeID,
            delay=delay,
            errDelay=errDelay,
            errCallback=errCallback,
        )

    def recv(self, noack=False, block=True, count=1, consumeID=">"):
        return self.client.recvMessages(
            self.options["recvQueue"],
            group=self.options["group"],
            consumer=self.name,
            noack=noack,
            block=block,
            count=count,
            consumeID=consumeID,
        )

    def send(self, msg):
        print("Send to `{}`: {}".format(self.options["sendQueue"], msg))
        return self.client.sendMessage(self.options["sendQueue"], data=msg)

    def sendSuccessMessage(self, msg):
        msg.update(success="true")
        return self.send(msg)

    def sendFailureMessage(self, msg):
        msg.update(success="false")
        return self.send(msg)

    def get(self, key):
        return self.kvclient.get(key)

    def set(self, key, value, expire=None, exist=None):
        expireParams = (
            {"ex": expire / 1000} if expire % 1000 else {"px": expire} if expire else {}
        )
        existParams = (
            {"xx": True} if exist else {"nx": True} if isinstance(exist, bool) else {}
        )
        params = dict(expireParams, existParams)
        return self.kvclient.set(key, value, **params)

    def delete(self, key):
        return self.kvclient.delete(key)


class RedisMQClient(object):
    def __init__(
        self, host="localhost", port=6379, options=None, client=None, realtime=False
    ):
        self.options = options or {}
        self.options.update(host=host, port=port, realtime=realtime)
        if client and not isinstance(client, redis.Redis):
            raise Exception("Invalid client: {}".format(client))
        self.client = client or redis.Redis(
            host=self.options["host"], port=self.options["port"], decode_responses=True
        )

    @property
    def connected(self):
        return bool(self.client.connection)

    def createQueue(self, name, group="default", consumeID="0"):
        try:
            return self.client.xgroup_create(name, group, id=consumeID, mkstream=True)
        except:
            traceback.print_exc()
            raise Exception("Queue existed: {}".format(name))

    def deleteQueue(self, *names):
        return self.client.delete(*names)

    # def hasQueue(self, name, group="default"):
    #     try:
    #         queue = self.client.xinfo_stream(name)
    #         groups = self.client.xinfo_groups(name)
    #         return any(g["name"].decode() == group for g in groups)
    #     except:
    #         return False

    def sendMessage(self, queue, data, messageID="*", maxlen=None):
        return self.client.xadd(queue, data, id=messageID, maxlen=maxlen)

    def recvMessages(
        self,
        queue,
        group="default",
        consumer="unknown",
        noack=False,
        block=True,
        count=1,
        consumeID=">",
    ):
        block = None if not block else 0 if block is True else block
        return self.client.xreadgroup(
            group, consumer, {queue: consumeID}, count=count, block=block, noack=noack
        )

    def subscribeQueue(
        self,
        queue,
        group="default",
        consumer="unknown",
        noack=False,
        block=True,
        count=1,
        consumeID=">",
        delay=1,
        errDelay=1,
        errCallback=print,
    ):
        def _parseMessagesGenerator(messages):
            for message in messages:
                _queue, items = message
                for item in items:
                    _id, _data = item
                    yield {"id": _id, "data": _data, "queue": _queue, "group": group}

        while True:
            try:
                messages = self.recvMessages(
                    queue,
                    group=group,
                    consumer=consumer,
                    noack=noack,
                    block=block,
                    count=count,
                    consumeID=consumeID,
                )
                messages = list(_parseMessagesGenerator(messages))
            except:
                traceback.print_exc()
                time.sleep(errDelay)
                continue
            if messages:
                for message in messages:
                    yield message
                self.client.xack(queue, group, *[m["id"] for m in messages])
            else:
                time.sleep(delay)
