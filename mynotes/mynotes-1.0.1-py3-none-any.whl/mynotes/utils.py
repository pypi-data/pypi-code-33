"""Utility functions."""

# mynotes builds indexes and converts to HTML a tree of notes written in
# Markdown.
# Copyright (C) 2018 Yorick Brunet <mynotes@yok.ch>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

import os
from typing import Iterator, List, Tuple
from dataclasses import dataclass


def walk(top: str,
         excl_dirs: List[str],
         excl_files: List[str]
         ) -> Iterator[Tuple[str, List[str], List[str]]]:
    """Generate data from os.walk while exlcuding files/dirs.

    :param str top: Root directory
    :param list[str] excl_dirs: Excluded directories
    :param list[str] excl_files: Excluded files
    :return: Tuple root, dirs, files for each visited directory
    :rtype: tuple[str, list[str], list[str]]
    """
    for root, dirs, files in os.walk(top, topdown=True):
        dirs[:] = [d for d in dirs if d not in excl_dirs]
        files[:] = [f for f in files if f not in excl_files]
        yield root, dirs, files


@dataclass
class Params:
    """Parameters for mynotes package classes and methods.

    Contains parameters from :ref:`Config` and extra arguments given to cli
    interfaces directly.

    :var str index: Index file
    :var str home: Home file
    :var str md_ext: Markdown extension
    :var list[str] excl_dirs: Excluded directories
    :var list[str] excl_files: Excluded files
    :var bool verbose: Increase verbosity
    """

    index: str
    home: str
    md_ext: str
    excl_dirs: List[str]
    excl_files: List[str]
    verbose: bool


class DataAbstract:
    """Abstract data. Must be subclassed.

    :var str index: Index file (from configuration)
    :var str home: Home file (from configuration)
    :var str root: Root path of the file
    :var str name: File name
    :var str title: File title
    :param str index: Index file (from configuration)
    :param str home: Home file (from configuration)
    :param str root: Root path of the file
    :param str name: File name
    :param str title: File title
    """

    def __init__(self,
                 home: str,
                 index: str,
                 root: str,
                 name: str,
                 title: str) -> None:
        self._home = home
        self._index = index
        self.root = root
        self.name = name
        self.title = title

    def compare(self) -> str:
        """Return value to compare this object with others.

        :return: Value for comparison
        :rtype: str
        """
        return self.title.lower()

    def is_home_file(self) -> bool:
        """Indicate whether this file is the :ref:`HOME_FILE`.

        :return: True if it is the :ref:`HOME_FILE, False otherwise.
        :rtype: bool
        """
        return self.name == self._home

    def __repr__(self):
        """Class representation."""
        return f'{self.__class__.__name__}(' \
               f'\'{self._home}\', ' \
               f'\'{self._index}\', ' \
               f'\'{self.root}\', ' \
               f'\'{self.name}\', ' \
               f'\'{self.title}\')'


class DataFile(DataAbstract):
    """File data."""

    def __init__(self,
                 home: str,
                 index: str,
                 root: str,
                 name: str,
                 title: str) -> None:
        super().__init__(home, index, root, name, title)

    def link(self) -> str:
        """Return file link.

        :return: File link
        :rtype: str
        """
        return f'[{self.title}]({self.name})'


class DataDir(DataAbstract):
    """Directory data.

    Directory name and directory title are identical.
    """

    def __init__(self,
                 home: str,
                 index: str,
                 root: str,
                 name: str,
                 title: str) -> None:
        super().__init__(home, index, root, name, title)

    def link(self) -> str:
        """Return directory link.

        :return: Directory link
        :rtype: str
        """
        return f'[{self.title}]({self.name}/{self._index})'


# autoapi.sphinx directive
__api__ = [
    'walk',
    'Params',
    'DataAbstract',
    'DataFile',
    'DataDir',
]
