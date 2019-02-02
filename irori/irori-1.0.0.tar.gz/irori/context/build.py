import pathlib
import enum
import argparse

from . import base
from irori.depend import Dependencies


class Mode(enum.Enum):
    debug = 'debug'
    release = 'release'


class BuildContext(base.Context):
    def __init__(self,
                 obj: pathlib.Path,
                 output: pathlib.Path, mode: Mode, dependencies: Dependencies, args: argparse.Namespace):
        self.__object_dir = obj
        self.__output_file = output
        self.__mode = mode
        self.__dependencies = dependencies
        self.__args = args

    @property
    def object_directory(self) -> pathlib.Path:
        return self.__object_dir

    @property
    def output_file(self) -> pathlib.Path:
        return self.__output_file

    @property
    def mode(self) -> Mode:
        return self.__mode

    @property
    def is_debug(self) -> bool:
        return self.mode == Mode.debug

    @property
    def is_release(self) -> bool:
        return self.mode == Mode.release

    @property
    def dependencies(self) -> Dependencies:
        return self.__dependencies

    @property
    def arguments(self) -> argparse.Namespace:
        return self.__args
