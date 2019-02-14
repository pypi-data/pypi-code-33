# coding=utf-8
from __future__ import print_function

import time
import traceback

import redis


class RedisMQ(object):
    def __init__(
        self,
        redisHost="localhost",
        redisPort=6379,
        redisRealtime=False,
        options=None,
        client=None,
        **kwargs
    ):
        self.options = options or {}
        self.options.update(host=redisHost, port=redisPort, realtime=redisRealtime)
        if client and not isinstance(client, redis.Redis):
            raise Exception("Invalid client: {}".format(client))
        self.client = client or redis.Redis(
            host=self.options["host"], port=self.options["port"], decode_responses=True
        )

    @property
    def connected(self):
        return bool(self.client.connection)

    def createQueue(self, name, group="default", consumeID="0", force=False):
        if force:
            self.deleteQueue(name)
        return self._createQueue(name, group=group, consumeID=consumeID)

    def _createQueue(self, name, group="default", consumeID="0"):
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
