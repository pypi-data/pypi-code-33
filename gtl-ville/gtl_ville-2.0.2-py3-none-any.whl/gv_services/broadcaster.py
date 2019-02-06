#!/usr/bin/env python3

import asyncio
import traceback


class Broadcaster:

    def __init__(self, logger):
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
                message = self.messages.get(datatype)
                nsubs.append(True)
                async with condition:
                    event.set()
                if message is not None:
                    await stream.send_message(message)
                    self.logger.debug('Broadcaster sent {} data.'.format(datatype))
                else:
                    self.logger.warning('Something went wrong while broadcasting {} data.'.format(datatype))
        except:
            pass
        finally:
            self.logger.info('Broadcaster lost a subscriber on {} data.'.format(datatype))

    async def publish(self, message):
        datatype = message.datatype
        self.logger.debug('Broadcaster received {} data.'.format(datatype))
        success = True
        transmited = False
        try:
            if await self.is_datatype_registered(datatype):
                lock = self.locks[datatype]
                async with lock:
                    condition = self.conditions[datatype]
                    ninitialsubs = len(condition._waiters)
                    if ninitialsubs > 0:
                        self.messages[datatype] = message.data
                        async with condition:
                            condition.notify_all()
                        transmited = True
                        event = self.events[datatype]
                        nsubs = self.nsubs[datatype]
                        while len(nsubs) < ninitialsubs:
                            await event.wait()
                            async with condition:
                                event.clear()
                        nsubs.clear()
                        del self.messages[datatype]
        except:
            success = False
            self.logger.error(traceback.format_exc())
            self.logger.error('An error occurred while forwarding {} data.'.format(datatype))
        finally:
            if not transmited:
                self.logger.warning('No subscriber for {} data.'.format(datatype))
            return success

    async def is_datatype_registered(self, datatype):
        async with self.lock:
            return datatype in self.datatypes
