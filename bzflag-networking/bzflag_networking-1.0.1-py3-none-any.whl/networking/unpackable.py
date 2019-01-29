from typing import BinaryIO


class Unpackable:
    def unpack(self, buf: BinaryIO) -> None:
        raise NotImplementedError()
