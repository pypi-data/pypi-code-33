#!/usr/bin/env python3

import asyncio
import traceback

from gv_services.broadcaster_grpc import BroadcasterBase
from gv_services.common_pb2 import pub_ack


class Broadcaster(BroadcasterBase):

    def __init__(self, logger):
        super().__init__()
        self.logger = logger
        self.lock = asyncio.Lock()
        self.datatypes = set()
        self.locks = {}
        self.conditions = {}
        self.events = {}
        self.nsubs = {}
        self.messages = {}

    async def subscribe(self, stream):
        request = await stream.recv_message()
        datatype = request.datatype
        self.logger.info('Broadcaster got a new subscriber on {} data.'.format(datatype))
        async with self.lock:
            if datatype not in self.datatypes:
                self.datatypes.add(datatype)
                self.locks[datatype] = asyncio.Lock()
                self.conditions[datatype] = asyncio.Condition()
                self.events[datatype] = asyncio.Event()
                self.nsubs[datatype] = list()
        condition = self.conditions[datatype]
        event = self.events[datatype]
        nsubs = self.nsubs[datatype]
        try:
            while True:
                async with condition:
                    await condition.wait()
                message = self.messages.get(datatype, '')
                nsubs.append(True)
                async with condition:
                    event.set()
                await stream.send_message(message)
                self.logger.info('Broadcaster sent {} data.'.format(datatype))
        except:
            pass
        finally:
            self.logger.info('Broadcaster lost a subscriber on {} data.'.format(datatype))

    async def publish(self, stream):
        message = await stream.recv_message()
        datatype = message.datatype
        self.logger.info('Broadcaster received {} data.'.format(datatype))
        success = False
        try:
            if await self.is_datatype_registered(datatype):
                lock = self.locks[datatype]
                async with lock:
                    condition = self.conditions[datatype]
                    ninitialsubs = len(condition._waiters)
                    if ninitialsubs > 0:
                        self.messages[datatype] = message
                        async with condition:
                            condition.notify_all()
                        success = True
                        event = self.events[datatype]
                        nsubs = self.nsubs[datatype]
                        while len(nsubs) < ninitialsubs:
                            await event.wait()
                            async with condition:
                                event.clear()
                        nsubs.clear()
                        del self.messages[datatype]
        except:
            self.logger.error(traceback.format_exc())
            self.logger.error('An error occurred while forwarding {} data.'.format(datatype))
        finally:
            if not success:
                self.logger.warning('No subscriber for {} data.'.format(datatype))
            await stream.send_message(pub_ack(success=success))

    async def is_datatype_registered(self, datatype):
        async with self.lock:
            return datatype in self.datatypes
