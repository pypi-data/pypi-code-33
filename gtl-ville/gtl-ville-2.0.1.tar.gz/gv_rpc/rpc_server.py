#!/usr/bin/env python3

import asyncio
import traceback

from grpclib.server import Server

from gv_services.archivist import Archivist
from gv_services.broadcaster import Broadcaster
from gv_services.interface import Interface
from gv_utils.asyncio import check_event_loop


class RpcServer:

    def __init__(self, logger):
        self.logger = logger
        self.server = None

    def start(self, datapath, host, port):
        check_event_loop()  # will create a new event loop if needed (if we are in a thread)
        self.logger.info('RPC server is starting.')
        try:
            asyncio.run(self._run(datapath, host, port))
        except KeyboardInterrupt:
            pass
        self.logger.info('RPC server has stopped.')

    async def _run(self, datapath, host, port):
        try:
            interface = Interface(self.logger, datapath)
            await interface.async_init()
            self.server = Server([interface], loop=asyncio.get_event_loop())
            await self._serve(host, port)
        except:
            self.logger.error(traceback.format_exc())

    async def _serve(self, host, port):
        await self.server.start(host, port)
        self.logger.info('RPC server is serving on {}:{}.'.format(host, port))
        try:
            self.logger.info('RPC server has started.')
            await self.server.wait_closed()  # block until an exception is raised
        except asyncio.CancelledError:
            await self._close()

    async def _close(self):
        if self.server is not None:
            self.server.close()
            self.logger.info('RPC server is closing.')
            await self.server.wait_closed()
            self.server = None


def start(Application, threaded=False):
    if threaded:
        import threading
        threading.Thread(target=start, args=(Application, False), daemon=True).start()
        print('Starting application in a background thread...')
    else:
        Application()
