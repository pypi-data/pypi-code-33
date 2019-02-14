import struct
from io import UnsupportedOperation
from pathlib import Path
from typing import Iterable, List

from shapely.wkb import dumps, loads

from .fileformat_pb2 import Body, Tag


BYTEORDER = 'little'
COOKIE = b'SPAT'


class Feature(object):
    __slots__ = 'geometry', 'properties'

    def __init__(self, geometry, properties):
        self.geometry = geometry
        self.properties = properties

    def __repr__(self):
        return '{}: ({})'.format(self.geometry.geom_type, self.properties.__repr__())


class File(object):
    type_deserializers = {
        Tag.STRING: lambda buf: buf.decode('utf-8'),
        Tag.INT: lambda buf: int.from_bytes(buf, 'little'),
        Tag.DOUBLE: lambda buf: struct.unpack('d', buf)[0]
    }
    type_serializers = {
        str: lambda v: (v.encode('utf-8'), Tag.STRING),
        int: lambda v: (v.to_bytes(8, BYTEORDER), Tag.INT),
        float: lambda v: (struct.pack('d', v), Tag.DOUBLE)
    }
    blocksize = 100000

    def __init__(self, file, readonly=False):
        """Initialize a Spaten stream. If file is a str, it will be treated as a file
        path, otherwise it will be handled as a stream."""
        if isinstance(file, str):
            path = Path(file)
            if not readonly and not path.exists():
                path.touch()
            self.open = lambda: open(str(path), 'rb' if readonly else 'r+b')
            self._close = lambda: self.r.close()
        else:
            self.open = lambda: file  # assume this is already a stream: noop
            self._close = lambda: file

        if not readonly:
            self._wr_buf = []  # type: List[Feature]

    def __enter__(self):
        self.r = self.open()
        try:
            self.read_header()
        except (EOFError, UnsupportedOperation) as eof:
            try:
                self.write_header()
            except IOError:
                raise eof
        return self

    def __exit__(self, *args, **kwargs):
        self.close()

    def flush(self):
        if not hasattr(self, '_wr_buf') or not self._wr_buf:
            # if its a readonly stream or there is nothing to be written
            return
        self.write_block(self._wr_buf)
        self._wr_buf = []

    def close(self):
        self.flush()
        self._close()

    def parse_tags(self, tags) -> dict:
        props = {}
        for tag in tags:
            props[tag.key] = self.type_deserializers[tag.type](tag.value)
        return props

    def serialize_tags(self, tags) -> List[Tag]:
        serialized = []
        for k, v in tags.items():
            val, typ = self.type_serializers[type(v)](v)
            serialized.append(Tag(key=k, value=val, type=typ))
        return serialized

    def read(self, size: int):
        """Reads the specified number of bytes and checks if EOF has occured"""
        buf = self.r.read(size)
        if len(buf) != size:
            raise EOFError
        return buf

    def read_int(self, size: int) -> int:
        return int.from_bytes(self.read(size), BYTEORDER)

    def write(self, buf: bytes):
        self.r.write(buf)

    def write_int(self, i: int, size: int):
        self.write(i.to_bytes(size, BYTEORDER))

    def read_header(self):
        cookie = self.read(4)
        if cookie != COOKIE:
            raise ValueError('Invalid header')
        version = self.read_int(4)
        if version != 0:
            raise ValueError('The library only supports Spaten version 0')
        return version

    def write_header(self):
        self.write(COOKIE)
        self.write_int(0, 4)

    def read_block(self) -> List[Feature]:
        body_len = self.read_int(4)
        flags = self.read_int(2)
        compression = self.read_int(1)
        message_serialization = self.read_int(1)

        if compression != 0:
            raise AttributeError('compression in Spaten files not supported by library')

        if message_serialization != 0:
            raise AttributeError('non-protobuf Spaten files are not supported')

        bodybuf = self.read(body_len)
        block = Body()
        block.ParseFromString(bodybuf)

        features = []
        for feature in block.feature:
            features.append(Feature(
                geometry=loads(feature.geom),
                properties=self.parse_tags(feature.tags)
            ))
        return features

    def write_block(self, features: Iterable[Feature]):
        block = Body()
        for feat in features:
            block.feature.add(geom=dumps(feat.geometry), tags=self.serialize_tags(feat.properties))
        bodybuf = block.SerializeToString()

        self.write_int(len(bodybuf), 4)  # body size
        self.write_int(0, 2)  # flags
        self.write_int(0, 1)  # compression
        self.write_int(0, 1)  # message type
        self.write(bodybuf)

    def __iter__(self):
        self._rd_buf = []  # type: List[Feature]
        if not hasattr(self, 'r'):
            # The file hasn't been opened before, so let's prepare the reader.
            # _auto_open is used in order to close the file automatically later with a context manager.
            self.__enter__()
            self._auto_open = True
        return self

    def __next__(self) -> Feature:
        try:
            if len(self._rd_buf) == 0:
                self._rd_buf = self.read_block()
            return self._rd_buf.pop(0)
        except EOFError:
            if hasattr(self, '_auto_open') and self._auto_open:
                self.__exit__()
            raise StopIteration

    def append(self, feature: Feature):
        self._wr_buf.append(feature)
        if len(self._wr_buf) >= self.blocksize:
            self.flush()
