""" This code is released under the terms, conditions, and limitations of
GNU Affero General Public License Version 3.0 or later

Author: Rigel Kent
Date: 29th, january 2019
"""

import os
import asyncio
import threading
import websockets
import pathlib
from promise import Promise, set_default_scheduler
from promise.schedulers.asyncio import AsyncioScheduler

from .sock import WSClient
from .daemon_pb2 import Instruction, Subject, Answer


set_default_scheduler(AsyncioScheduler())


class DatDaemonClient:

    def __init__(self, url="ws://{}:{}".format(os.getenv('DAT_DAEMON_HOST', 'localhost'), os.getenv('DAT_DAEMON_PORT', 8477)), sock=None):
        # deciding wether to use the url or the socket client
        self.url = url if not sock else None
        self.sock = sock if sock else None

        # storing the client
        self.client = None

        # This stores promised by "id", is used to route the answer to the correct resolution
        self.router = dict()
        self.id = 0

        # pre-start a single thread that runs the asyncio event loop
        self.bgloop = asyncio.new_event_loop()
        self._thread = threading.Thread(target=self.bgloop.run_forever)
        self._thread.daemon = True
        self._thread.start()

    async def init_receive_task(self):
        self.receive_task = self.bgloop.create_task(self.__receive())

    def run(self):
        # use run_coroutine_threadsafe to safely submit a coroutine
        # to the event loop running in a different thread
        init_done = asyncio.run_coroutine_threadsafe(
            self.init_receive_task(),
            self.bgloop
        )
        # wait for the init coroutine to actually finish
        init_done.result()
        return self

    def stop(self):
        # Cancel the running task. Since the event loop is in a
        # background thread, request cancellation with
        # call_soon_threadsafe.
        self.bgloop.call_soon_threadsafe(self.receive_task.cancel)

    @staticmethod
    def __openUrl(uri: str):
        return websockets.connect(uri)

    @staticmethod
    def __openSocket(sock: pathlib.Path):
        return WSClient(path=sock)

    async def __receive(self):
        # keep_running is not needed - cancel the task instead
        while True:
            if not self.client or not self.client.connected:
                self.client = await self.__openUrl(self.url) if self.url else await self.__openSocket(self.sock)
                if self.client.open:
                    print('Connection stablished. Client correcly connected.')

            recv_data = await self.client.recv()
            answer = Answer.ParseFromString(recv_data)

            print(answer)
            self.router.get(answer['id'])(answer)  # apply function for operation id

    async def __send(self, data):
        if not self.client or not self.client.connected:
            self.client = await self.__openUrl(self.url) if self.url else await self.__openSocket(self.sock)
        await self.client.send(data)

    # route
    def route(self, id: int, transform=lambda x: x):
        """
        Transform and set the data received for operation id
        """
        def resolver(res, rej):
            def _route(data):
                if id in self.router:
                    del self.router[id]
                if data['failure'] == 1:
                    rej('operaiton failed')
                self.router[id] = transform(data)
                res(self.router[id])

            self.router[id] = _route

        return Promise(resolver)

    # list
    async def list(self):
        self.id += 1
        current = self.id

        await self.__send(Instruction(
            subject=Subject.Value('LIST'),
            action=Instruction.Action.Value('GET'),
            id=current
        ).SerializeToString())

        return self.route(current, transform=lambda data: data['list'])

    # add
    async def add(self, path, key=None):
        self.id += 1
        current = self.id

        if key:
            await self.__send(Instruction(
                subject=Subject.Value('LIST'),
                action=Instruction.Action.Value('ADD'),
                key=key,
                id=current
                ).SerializeToString())
        else:
            await self.__send(Instruction(
                subject=Subject.Value('LIST'),
                action=Instruction.Action.Value('ADD'),
                path=path,
                id=current
                ).SerializeToString())

        return self.route(current)

    # removeList
    async def removeList(self, key):
        self.id += 1
        current = self.id

        await self.__send(Instruction(
            subject=Subject.Value('LIST'),
            action=Instruction.Action.Value('REMOVE'),
            key=key,
            id=current
        ).SerializeToString())

        return self.route(current)

    # start
    async def start(self, key):
        self.id += 1
        current = self.id

        await self.__send(Instruction(
            subject=Subject.Value('ITEM'),
            action=Instruction.Action.Value('START'),
            key=key,
            id=current
        ).SerializeToString())

        return self.route(current)

    # remove
    async def remove(self, key):
        self.id += 1
        current = self.id

        await self.__send(Instruction(
            subject=Subject.Value('ITEM'),
            action=Instruction.Action.Value('REMOVE'),
            key=key,
            id=current
        ).SerializeToString())

        return self.route(current)

    # load
    async def load(self, key):
        self.id += 1
        current = self.id

        await self.__send(Instruction(
            subject=Subject.Value('ITEM'),
            action=Instruction.Action.Value('LOAD'),
            key=key,
            id=current
        ).SerializeToString())

        return self.route(current)

    # watch
    async def watch(self, key):
        self.id += 1
        current = self.id

        await self.__send(Instruction(
            subject=Subject.Value('ITEM'),
            action=Instruction.Action.Value('WATCH'),
            key=key,
            id=current
        ).SerializeToString())

        return self.route(current)

    # mkdir
    async def mkdir(self, key, path):
        self.id += 1
        current = self.id

        await self.__send(Instruction(
            subject=Subject.Value('ITEM'),
            action=Instruction.Action.Value('MKDIR'),
            path=path,
            key=key,
            id=current
        ).SerializeToString())

        return self.route(current)

    # readdir
    async def readdir(self, key, path=''):
        self.id += 1
        current = self.id

        await self.__send(Instruction(
            subject=Subject.Value('ITEM'),
            action=Instruction.Action.Value('READDIR'),
            path=path,
            key=key,
            id=current
        ).SerializeToString())

        return self.route(current)

    # rmdir
    async def rmdir(self, key, path):
        self.id += 1
        current = self.id

        await self.__send(Instruction(
            subject=Subject.Value('ITEM'),
            action=Instruction.Action.Value('RMDIR'),
            path=path,
            key=key,
            id=current
        ).SerializeToString())

        return self.route(current)

    # unlink
    async def unlink(self, key, path):
        self.id += 1
        current = self.id

        await self.__send(Instruction(
            subject=Subject.Value('ITEM'),
            action=Instruction.Action.Value('UNLINK'),
            path=path,
            key=key,
            id=current
        ).SerializeToString())

        return self.route(current)

    # info
    async def info(self, key):
        self.id += 1
        current = self.id

        await self.__send(Instruction(
            subject=Subject.Value('ITEM'),
            action=Instruction.Action.Value('INFO'),
            key=key,
            id=current
        ).SerializeToString())

        return self.route(current)

    # createReadStream
    def createReadStream(self, key, path):
        return "{url}/{key}/read/{path}".format(url=self.url, key=key, path=path)

    # createWriteStream
    def createWriteStream(self, key, path):
        return "{url}/{key}/write/{path}".format(url=self.url, key=key, path=path)
