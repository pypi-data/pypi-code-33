import asyncio
import datetime
import functools
import logging
import string

import aiohttp
from unicodedata import category

logger = logging.getLogger(__name__)


class CloudLogger:
    allowed_white_spaces = set(['\n', '\t'])

    @classmethod
    def get_printable(cls, x):
        # https://stackoverflow.com/a/19016117/133568
        if isinstance(x, bytes):
            x = x.decode('utf-8')
        return ''.join([s for s in x if s in cls.allowed_white_spaces or category(s)[0] != "C"])

    def __init__(self, endpoint, loop=None):
        self.endpoint = endpoint
        self.loop = loop or asyncio.get_event_loop()
        self.session = aiohttp.ClientSession(loop=self.loop)
        self.tasks = {}

    def __enter__(self):
        raise TypeError("Use async with instead")

    def __exit__(self, exc_type, exc_val, exc_tb):
        # __exit__ should exist in pair with __enter__ but never executed
        pass  # pragma: no cover

    async def __aenter__(self):
        return self

    async def close(self, grace_seconds=10):
        if self.tasks:
            logger.debug('Remote logger is closing but still has %s tasks, will allow %s seconds of grace', len(self.tasks), grace_seconds)
            await asyncio.sleep(grace_seconds)
            if self.tasks:
                logger.info('Remote logger is closing and %s tasks, are still alive after the grace period', len(self.tasks))
        for task in self.tasks:
            task.cancel()

        await self.session.close()
        await  asyncio.sleep(0.25)

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.close()

    def _on_done(self, log_line: str, done_task: asyncio.Task):
        # noinspection PyBroadException
        try:
            done_task.result()
            logger.debug('%s: sent: %s', self.endpoint, log_line)
        except asyncio.CancelledError:
            logger.info('Line %s was not sent to server, the send task was cancelled', log_line)
        except asyncio.InvalidStateError:
            logger.info("Line %s was not sent to server, the send task hasn't started", log_line)
        except aiohttp.client_exceptions.ClientConnectorError as ex:
            logger.info('Failed to send "%s" to ML: %s', log_line, str(ex))
        except Exception:
            logger.exception('Failed to post log line %s', log_line)
        del (self.tasks[done_task])

    async def on_log(self, line, step_name=None):
        printable = self.get_printable(line)
        if not printable:
            return

        log_level = 'INFO' if step_name == 'Run Code' else 'DEBUG'
        task = asyncio.ensure_future(self.session.post(url=self.endpoint, json={'level': log_level, 'message': printable, 'category': step_name or 'CloudLogger', 'ts': datetime.datetime.utcnow().isoformat()}), loop=self.loop)
        task.add_done_callback(functools.partial(self._on_done, line))
        self.tasks[task] = True
