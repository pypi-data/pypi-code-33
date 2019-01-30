# coding: UTF-8

from ctypes import py_object
from typing import Tuple, Union

from linux_aio_bind import IOEvent

from .command import AIOCmd, NonVectorCmd, ReadCmd, ReadVCmd, VectorCmd, WriteCmd, WriteVCmd


class AIOEvent:
    """
    .. versionadded:: 0.1.0
    """
    __slots__ = ('_event', '_aio_block')

    _event: IOEvent
    _aio_block: AIOCmd

    def __init__(self, event: IOEvent) -> None:
        self._event = event
        self._aio_block = py_object.from_address(self._event.data).value

    @property
    def aio_block(self) -> AIOCmd:
        return self._aio_block

    @property
    def buffer(self) -> Union[None, VectorCmd.BUF_TYPE, NonVectorCmd.BUF_TYPE]:
        if isinstance(self._aio_block, (ReadCmd, WriteCmd, ReadVCmd, WriteVCmd)):
            return self._aio_block.buffer
        else:
            return None

    def stripped_buffer(self) -> Union[None, VectorCmd.BUF_TYPE, NonVectorCmd.BUF_TYPE]:
        """`\0` pads removed buffer"""
        buffer = self.buffer

        if isinstance(buffer, (bytearray, bytes)):
            return buffer.rstrip(b'\0')
        elif isinstance(buffer, Tuple):
            # TODO: implement me
            raise NotImplementedError('Stripping of buffer vector is not implemented yet.')
        else:
            return None

    @property
    def response(self) -> int:
        return self._event.res

    @property
    def response2(self) -> int:
        return self._event.res2
