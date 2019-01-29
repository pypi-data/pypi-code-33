""" This code is released under the terms, conditions, and limitations of
BSD 3-Clause "New" or "Revised" License

Author: Hunter Prendergast
Date: December 31, 2018
"""
import socket
import websockets


class WSClient(object):
    """Async context manager for unix domain socket based websocket client.

    Usage:
    >>> import asyncio as aio
    >>> async def example():
    ...        async with WSClient(path='/tmp/sock.sock') as ws:
    ...            async for msg in ws:
    ...                print(msg)
    ...
    >>> loop = aio.get_event_loop()
    >>> loop.run_until_complete(example())
    """

    __slots__ = ["_host", "_path", "_port", "_ws"]

    def __init__(self, path=None, host=None, port=None):
        """Initialize context manager."""
        assert path or all([host, port]), "Must supply host and port or path."
        self._path = path
        self._host = host
        self._port = port
        self._ws = None

    async def __aenter__(self):
        """Entrance block."""
        if self._path:
            sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
            sock.connect(self._path)
            uri = "ws://localhost"
        else:
            sock = None
            uri = "ws://{}:{}".format(self._host, self._port)
        self._ws = await websockets.connect(uri, sock=sock)
        return self._ws

    async def __aexit__(self, exc_type, exc, tb):
        """Exit block."""
        await self._ws.close()

