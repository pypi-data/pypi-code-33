# Copyright 2018 leoetlino <leo@leolam.fr>
# Licensed under GPLv2+
import io
import math
from operator import itemgetter
from pathlib import Path
import struct
import typing

_NUL_CHAR = b'\x00'
_FileEntry = struct.Struct('>IIII')

class Tmpk:
    class File(typing.NamedTuple):
        offset: int
        data: memoryview

    def __init__(self, data: typing.Union[bytes, memoryview]) -> None:
        self._data = memoryview(data)
        self._files: typing.Dict[str, Tmpk.File] = dict()

        magic = self._data[0:4]
        if magic != b'TMPK':
            raise ValueError("Invalid magic: %s (expected 'TMPK')" % magic)

        num_files = self._read_u32(4)
        offset = 0x10
        for i in range(num_files):
            name_offset, file_offset, file_size, _ = _FileEntry.unpack_from(self._data, offset)
            name = self._read_string(name_offset)
            self._files[name] = self.File(offset=file_offset,
                                          data=self._data[file_offset:file_offset+file_size])
            offset += _FileEntry.size

    def get_files(self) -> typing.Dict[str, File]:
        return self._files

    def get_file_offsets(self) -> typing.List[typing.Tuple[str, int]]:
        offsets: list = []
        for name, file in self._files.items():
            offsets.append((name, file.offset))
        return sorted(offsets)

    def guess_default_alignment(self) -> int:
        if len(self._files) <= 2:
            return 4
        gcd = next(iter(self._files.values())).offset
        for node in self._files.values():
            gcd = math.gcd(gcd, node.offset)
        return gcd

    def _read_u32(self, offset: int) -> int:
        return struct.unpack_from('>I', self._data, offset)[0]
    def _read_string(self, offset: int) -> str:
        end = self._data.obj.find(_NUL_CHAR, offset) # type: ignore
        return bytes(self._data[offset:end]).decode('utf-8')

def _align_up(n: int, alignment: int) -> int:
    return (n + alignment - 1) & -alignment

def _write(stream: typing.BinaryIO, data: bytes, offset: int) -> int:
    current_pos = stream.tell()
    stream.seek(offset)
    stream.write(data)
    stream.seek(current_pos)
    return len(data)

class TmpkWriter:
    class File(typing.NamedTuple):
        name: str
        data: typing.Union[memoryview, bytes]

    def __init__(self) -> None:
        self._files: typing.Dict[str, TmpkWriter.File] = dict()
        self._default_alignment = 4

    def set_default_alignment(self, alignment: int) -> None:
        self._default_alignment = alignment

    def add_file(self, name: str, data) -> None:
        self._files[name] = self.File(name, data)

    def delete_file(self, name: str) -> None:
        del self._files[name]

    def _get_alignment_for_file(self, file: File) -> int:
        extension = Path(file.name).suffix
        if extension == '.gmx':
            return 0x40
        if extension == '.gtx':
            return 0x1000
        return self._default_alignment

    def get_file_offsets(self) -> typing.List[typing.Tuple[str, int]]:
        offsets: list = []
        data_offset = 0x10 + _FileEntry.size * len(self._files)
        sorted_names = sorted(self._files.keys())
        for name in sorted_names:
            data_offset += len(name) + 1
        for name in sorted_names:
            alignment = self._get_alignment_for_file(self._files[name])
            data_offset = _align_up(data_offset, alignment)
            offsets.append((name, data_offset))
            data_offset += len(self._files[name].data)
        return offsets

    def write(self, stream: typing.BinaryIO) -> int:
        # TMPK header
        stream.write(b'TMPK')
        stream.write(self._u32(len(self._files)))
        stream.write(self._u32(0x1000)) # TODO: what is this?
        stream.write(self._u32(0)) # TODO: Padding?

        # File information
        file_list_offset = stream.tell()
        stream.seek(_FileEntry.size * len(self._files), io.SEEK_CUR)

        # File name list
        sorted_names = sorted(self._files)
        for i, name in enumerate(sorted_names):
            _write(stream, self._u32(stream.tell()), file_list_offset + 0x10*i)
            stream.write(name.encode())
            stream.write(_NUL_CHAR)

        # File data
        max_alignment = 1
        for i, name in enumerate(sorted_names):
            file = self._files[name]
            alignment = self._get_alignment_for_file(file)
            max_alignment = max(max_alignment, alignment)
            stream.seek(_align_up(stream.tell(), alignment))
            offset = file_list_offset + 0x10*i
            _write(stream, self._u32(stream.tell()), offset + 4)
            _write(stream, self._u32(len(file.data)), offset + 8)
            _write(stream, self._u32(0), offset + 12)
            stream.write(file.data) # type: ignore

        return max_alignment

    def _u32(self, value: int) -> bytes:
        return struct.pack('>I', value)

def make_writer_from_tmpk(tmpk: Tmpk) -> TmpkWriter:
    writer = TmpkWriter()
    writer.set_default_alignment(tmpk.guess_default_alignment())
    for name, file in tmpk.get_files().items():
        writer.add_file(name, file.data)
    return writer
