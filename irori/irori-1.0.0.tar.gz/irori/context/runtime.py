import typing
import pathlib

from .base import Context


class RuntimeContext(Context):
    def __init__(self, sources: typing.List[pathlib.Path]):
        self.__sources = sources
        self.__original_sources = sources
        self.__current = None
        self.__next = self.__sources[0]

    def consume(self, count=1) -> typing.List[pathlib.Path]:
        self.__current = self.__sources[:count]
        self.__sources = self.__sources[count:]
        if self.is_remaining:
            self.__next = self.__sources[0]
        else:
            self.__next = None
        return self.__current

    def consume_all(self) -> typing.List[pathlib.Path]:
        sources = self.__sources
        self.__sources = []
        return sources

    @property
    def remaining_count(self) -> int:
        return len(self.__sources)

    @property
    def is_remaining(self):
        return self.remaining_count > 0

    @property
    def remaining(self):
        return self.__sources

    @property
    def sources(self):
        return self.__original_sources

    @property
    def current(self):
        return self.__current

    @property
    def next(self):
        return self.__next
