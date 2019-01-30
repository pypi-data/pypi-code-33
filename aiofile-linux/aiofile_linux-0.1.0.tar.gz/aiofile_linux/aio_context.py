# coding: UTF-8

from __future__ import annotations

import asyncio
from ctypes import POINTER, c_long, c_uint, pointer
from types import TracebackType
from typing import ContextManager, Generator, Optional, Tuple, Type

from linux_aio_bind import IOEvent, aio_context_t, create_c_array, io_destroy, io_getevents, io_setup, io_submit, iocb_p

from .aio_event import AIOEvent
from .command import AIOCmd

_io_event_p = POINTER(IOEvent)


class AIOContext(ContextManager):
    """
    .. versionadded:: 0.1.0
    """
    __slots__ = ('_ctx', '_max_jobs')

    _ctx: aio_context_t
    _max_jobs: int

    def __init__(self, max_jobs: int) -> None:
        self._ctx = aio_context_t()
        self._max_jobs = max_jobs

        io_setup(c_uint(max_jobs), pointer(self._ctx))

    def __del__(self) -> None:
        self.close()

    @property
    def closed(self) -> bool:
        return self._ctx.value is 0

    def close(self) -> None:
        """will command on the completion of all operations that could not be canceled"""
        if not self.closed:
            io_destroy(self._ctx)
            self._ctx = aio_context_t()

    # noinspection PyProtectedMember
    @asyncio.coroutine
    def submit(self, *cmds: AIOCmd) -> Generator[None, None, Tuple[AIOEvent, ...]]:
        for cmd in cmds:
            if cmd._deleted:
                raise ValueError(
                        f'{cmd} can not be used because it has already been transformed into another AIOCmd.')

        submitted_cmd = io_submit(
                self._ctx,
                c_long(len(cmds)),
                create_c_array(iocb_p, (pointer(block._iocb) for block in cmds))
        )

        event_buf = create_c_array(IOEvent, (), submitted_cmd)

        tot_done_jobs = 0
        remaining_jobs = submitted_cmd

        while remaining_jobs is not 0:
            yield
            completed_jobs = io_getevents(
                    self._ctx,
                    c_long(0),
                    c_long(remaining_jobs),
                    _io_event_p(event_buf[tot_done_jobs]),
                    None
            )

            tot_done_jobs += completed_jobs
            remaining_jobs -= completed_jobs

        return tuple(AIOEvent(event) for event in event_buf[:tot_done_jobs])

    def __enter__(self) -> AIOContext:
        return self

    def __exit__(self, t: Optional[Type[BaseException]], value: Optional[BaseException],
                 traceback: Optional[TracebackType]) -> None:
        self.close()
