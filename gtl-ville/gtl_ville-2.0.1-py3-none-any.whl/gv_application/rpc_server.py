#!/usr/bin/env python3

import asyncio

from grpclib.server import Server

from gv_services.broadcaster import Broadcaster


class RpcServer:

    def __init__(self, logger):
        self.logger = logger
        self.server = None

    def start(self, host, port, ssl=None):
        try:
            self.logger.info('RPC server is starting.')
            asyncio.run(self.run(host, port, ssl))
        except:
            pass
        finally:
            self.logger.info('RPC server has stopped.')

    async def run(self, host, port, ssl):
        self.server = Server([Broadcaster(self.logger)], loop=asyncio.get_event_loop())
        await self.serve(host, port, ssl)

    async def serve(self, host, port, ssl):
        await self.server.start(host, port, ssl=ssl)
        self.logger.info('RPC server is serving on {}:{}.'.format(host, port))
        try:
            await self.server.wait_closed()
        except:
            pass
        finally:
            self.server.close()
            self.logger.info('RPC server is closing.')
            await self.server.wait_closed()
