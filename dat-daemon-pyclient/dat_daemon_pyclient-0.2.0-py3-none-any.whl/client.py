# -*- coding: utf-8 -*-
"""dat-daemon API Bindings for Python.

Classes:
 * DatDaemonClient – a Websocket client for interacting with a dat-daemon

This code is released under the terms, conditions, and limitations of
GNU Affero General Public License Version 3.0 or later

Author: Rigel Kent
Date: 29th, january 2019
"""

import os
import asyncio
import websockets
from protobuf_to_dict import protobuf_to_dict
from functools import wraps

from .daemon_pb2 import Instruction, Subject, Answer


class DatDaemonClient:

    def __init__(self, url="ws://{}:{}".format(os.getenv('DAT_DAEMON_HOST', 'localhost'), os.getenv('DAT_DAEMON_PORT', 8477))):
        self.url = url

    def dat_command(func):
        @wraps(func)
        def run(self, *args, **kwargs):
            loop = asyncio.get_event_loop()
            ret = loop.run_until_complete(asyncio.gather(func(self, *args, **kwargs)))
            return ret[0]  # loop wraps return values in a list… ><

        return run

    @staticmethod
    async def parse(client):
        answer = Answer()
        answer.ParseFromString(await client.recv())
        client.close()
        return protobuf_to_dict(answer)

    # list
    @dat_command
    async def list(self):
        client = await websockets.connect(self.url)

        await client.send(Instruction(
            subject=Subject.Value('LIST'),
            action=Instruction.Action.Value('GET'),
            id=0
        ).SerializeToString())

        return await self.parse(client)

    # add
    @dat_command
    async def add(self, path, key=None):
        client = await websockets.connect(self.url)

        if key:
            await client.send(Instruction(
                subject=Subject.Value('LIST'),
                action=Instruction.Action.Value('ADD'),
                path=path,
                key=key,
                id=0
                ).SerializeToString())
        else:
            await client.send(Instruction(
                subject=Subject.Value('LIST'),
                action=Instruction.Action.Value('ADD'),
                path=path,
                id=0
                ).SerializeToString())

        return await self.parse(client)

    # removeList
    @dat_command
    async def remove_list(self, key):
        client = await websockets.connect(self.url)

        await client.send(Instruction(
            subject=Subject.Value('LIST'),
            action=Instruction.Action.Value('REMOVE'),
            key=key,
            id=0
        ).SerializeToString())

        return await self.parse(client)

    # start
    @dat_command
    async def start(self, key):
        client = await websockets.connect(self.url)

        await client.send(Instruction(
            subject=Subject.Value('ITEM'),
            action=Instruction.Action.Value('START'),
            key=key,
            id=0
        ).SerializeToString())

        return await self.parse(client)

    # remove
    @dat_command
    async def remove(self, key):
        client = await websockets.connect(self.url)

        await client.send(Instruction(
            subject=Subject.Value('ITEM'),
            action=Instruction.Action.Value('REMOVE'),
            key=key,
            id=0
        ).SerializeToString())

        return await self.parse(client)

    # load
    @dat_command
    async def load(self, key):
        client = await websockets.connect(self.url)

        await client.send(Instruction(
            subject=Subject.Value('ITEM'),
            action=Instruction.Action.Value('LOAD'),
            key=key,
            id=0
        ).SerializeToString())

        return await self.parse(client)

    # watch
    @dat_command
    async def watch(self, key):
        client = await websockets.connect(self.url)

        await client.send(Instruction(
            subject=Subject.Value('ITEM'),
            action=Instruction.Action.Value('WATCH'),
            key=key,
            id=0
        ).SerializeToString())

        return await self.parse(client)

    # mkdir
    @dat_command
    async def mkdir(self, key, path):
        client = await websockets.connect(self.url)

        await client.send(Instruction(
            subject=Subject.Value('ITEM'),
            action=Instruction.Action.Value('MKDIR'),
            path=path,
            key=key,
            id=0
        ).SerializeToString())

        return await self.parse(client)

    # readdir
    @dat_command
    async def readdir(self, key, path=''):
        client = await websockets.connect(self.url)

        await client.send(Instruction(
            subject=Subject.Value('ITEM'),
            action=Instruction.Action.Value('READDIR'),
            path=path,
            key=key,
            id=0
        ).SerializeToString())

        return await self.parse(client)

    # rmdir
    @dat_command
    async def rmdir(self, key, path):
        client = await websockets.connect(self.url)

        await client.send(Instruction(
            subject=Subject.Value('ITEM'),
            action=Instruction.Action.Value('RMDIR'),
            path=path,
            key=key,
            id=0
        ).SerializeToString())

        return await self.parse(client)

    # unlink
    @dat_command
    async def unlink(self, key, path):
        client = await websockets.connect(self.url)

        await client.send(Instruction(
            subject=Subject.Value('ITEM'),
            action=Instruction.Action.Value('UNLINK'),
            path=path,
            key=key,
            id=0
        ).SerializeToString())

        return await self.parse(client)

    # info
    @dat_command
    async def info(self, key):
        client = await websockets.connect(self.url)

        await client.send(Instruction(
            subject=Subject.Value('ITEM'),
            action=Instruction.Action.Value('INFO'),
            key=key,
            id=0
        ).SerializeToString())

        return await self.parse(client)

    # createReadStream
    async def create_read_stream(self, key, path):
        return await websockets.connect("{url}/{key}/read/{path}".format(url=self.url, key=key, path=path))

    # createWriteStream
    async def create_write_stream(self, key, path):
        return await websockets.connect("{url}/{key}/write/{path}".format(url=self.url, key=key, path=path))
