# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# Copyright 2019 Daniel Mark Gass, see __about__.py for license information.
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

from ._dump import Dump


class UnpackError(Exception):
    """Data memory view error."""
    pass


class InsufficientMemoryError(UnpackError):
    """Too few memory bytes to create view of packed data memory."""
    pass


class ExcessMemoryError(UnpackError):
    """Leftover memory bytes after creating view of packed data memory."""

    def __init__(self, message, offset, extra_bytes):
        super(ExcessMemoryError, self).__init__(message, offset, extra_bytes)
        self.offset = offset
        self.extra_bytes = extra_bytes

    def __str__(self):
        return self.args[0]


class Memory:

    """Memory buffer view."""

    def __init__(self, buffer, offset=0):
        self.buffer = memoryview(buffer)
        assert 0 <= offset < self.buffer.nbytes
        self._offset = offset
        self.cursor = offset

    @property
    def consumed(self):
        return self.cursor - self._offset

    @property
    def available(self):
        return self.buffer.nbytes - self.cursor

    def unpack_and_getdump(self, cls):
        """Create view of packed data memory bytes.

        For example:
            >>> from plum import unpack
            >>> from plum.int.le import UInt8, UInt16
            >>> unpack(UInt16, b'0102')
            UInt16(513)

        :param type cls: view class
        :param bool dump: include view dump in any exception message
        :returns: view
        :rtype: type

        """
        dump = Dump(access='x')

        try:
            with self:
                item = cls.__unpack__(self, dump)

        except InsufficientMemoryError as exc:
            raise type(exc)(
                f'\n\n{dump.get_table()}\n\n{type(exc).__qualname__}: {exc}, '
                f'dump above shows interrupted progress',
                *exc.args[1:]).with_traceback(exc.__traceback__)

        except ExcessMemoryError as exc:
            for i in range(0, len(exc.extra_bytes), 16):
                dump.add_row(
                    value='<excess bytes>',
                    memory=exc.extra_bytes[i:i + 16])

            raise type(exc)(
                f'\n\n{dump.get_table()}\n\n{type(exc).__qualname__}: {exc}, '
                f'dump above shows interrupted progress',
                *exc.args[1:]).with_traceback(exc.__traceback__)

        except Exception as exc:
            raise UnpackError(
                f"\n\n{dump.get_table()}"
                f"\n\nUnpackError: unexpected {type(exc).__qualname__} "
                f"exception occurred during unpack operation, "
                f"dump above shows interrupted progress, original "
                f"exception traceback appears above this exception's "
                f"traceback"
            ).with_traceback(exc.__traceback__)

        return item, dump.get_table()

    def unpack(self, cls):
        """Create view of packed data memory bytes.

        For example:
            >>> from plum import unpack
            >>> from plum.int.le import UInt8, UInt16
            >>> unpack(UInt16, b'0102')
            UInt16(513)

        :param type cls: view class
        :param bool dump: include view dump in any exception message
        :returns: view
        :rtype: type

        """
        cursor = self.cursor
        try:
            with self:
                return cls.__unpack__(self, None)

        except Exception:
            # do it over to include dump in exception message
            self.cursor = cursor
            self.unpack_and_getdump(cls)
            assert 0, 'Internal Error'

    def setbytes(self, offset, buffer):
        self.buffer[offset:offset + len(buffer)] = buffer

    def getbytes(self, nbytes, offset=None, type=None, dump=None):
        # FUTURE: rename to consume_bytes
        if offset is None:
            start = self.cursor
            self.cursor += nbytes
        else:
            start = offset

        stop = start + nbytes

        buffer = self.buffer[start:stop]

        if dump:
            dump.memory = buffer
            if type:
                dump.cls = type

        if type and len(buffer) != nbytes:
            if dump:
                dump.value = '<insufficient bytes>'
            if offset is None:
                offset_message = ''
            else:
                offset_message = f'at byte offset {offset} '
            unpack_shortage = (
                f'{nbytes - len(buffer)} too few memory bytes to unpack '
                f'{type.__qualname__} {offset_message}'
                f'({nbytes} needed, only {len(buffer)} available)')
            raise InsufficientMemoryError(unpack_shortage)

        return buffer

    @property
    def readonly(self):
        return self.buffer.readonly

    @property
    def remote(self):
        return False

    def __enter__(self):
        self.cursor = self._offset
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if not exc_type:
            nbytes = self.buffer.nbytes
            if self.cursor != nbytes:
                msg = (
                    f'{nbytes - self.cursor} unconsumed memory bytes '
                    f'({nbytes - self._offset} available, '
                    f'{self.consumed} consumed)'
                )
                offset = self.cursor
                extra_bytes = self.buffer[self.cursor:]
                raise ExcessMemoryError(msg, offset, extra_bytes)
