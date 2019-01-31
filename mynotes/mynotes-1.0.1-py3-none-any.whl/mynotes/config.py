"""Manage configuration file."""

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

import configparser
from typing import List, Optional, Tuple

from . import constants as constants


class Config(configparser.ConfigParser):
    """Manage the configuration that is stored in configuration file.

    :param str file_: Configuration file path
    :var str _file: Configuration file path
    """

    PRM_MD_EXT = 'md_ext'
    """Name of parameter *markdown extension*, ref :ref:`MARKDOWN_EXT`."""
    PRM_INDEX = 'index'
    """Name of parameter *index*, ref :ref:`INDEX_FILE`."""
    PRM_HOME = 'home'
    """Name of parameter *home*, ref :ref:`HOME_FILE`."""
    PRM_EXCL_FILES = 'excl_files'
    """Name of parameter *exclude files*, ref :ref:`EXCLUDE_FILES`."""
    PRM_EXCL_DIRS = 'excl_dirs'
    """Name of parameter *exclude dirs*, ref :ref:`EXCLUDE_DIRS`."""
    PRM_PLUGINS_HTML = 'plugins_html'
    """Name of parameter *HTML plugins*, ref :ref:`PLUGINS_HTML`."""

    def __init__(self, file_: Optional[str] = None) -> None:
        super().__init__()
        if file_ is None:
            self._file = constants.CONFIG_FILE
        else:
            self._file = file_
        self.read(self._file)

    def write(self):
        """Write current configuration to file."""
        with open(self._file, 'w') as fpw:
            super().write(fpw)

    def _read_prm(self, prm: str, default: str) -> Tuple[str, bool]:
        """Read parameter from configuration.

        :param str prm: Name of the parameter
        :param str default: Default value
        :return: Parameter value and boolean indicating if parameter was just
            created
        :rtype: tuple[str, bool]
        """
        created = False
        # Section not present
        if constants.PACKAGE_NAME not in self:
            created = True
            self[constants.PACKAGE_NAME] = {}
        # Section present but parameter not present
        if prm not in self[constants.PACKAGE_NAME]:
            created = True
            self[constants.PACKAGE_NAME][prm] = default
        # Both present
        return self[constants.PACKAGE_NAME][prm], created

    def _update_prm(self, prm: str, default: str) -> str:
        """Read parameter from configuration and update config file if missing.

        :param str prm: Name of the parameter
        :param str default: Default value
        :return: Parameter value
        :rtype: str
        """
        val, crd = self._read_prm(prm, default)
        if crd:
            self.write()
        return val

    def markdown_ext(self) -> str:
        """Return the markdown extension from configuration.

        :return: Markdown extension
        :rtype: str
        """
        return self._update_prm(self.PRM_MD_EXT, constants.MARKDOWN_EXT)

    def index_file(self) -> str:
        """Return the index file from configuration.

        :return: Index file
        :rtype: str
        """
        return self._update_prm(self.PRM_INDEX, constants.INDEX_FILE)

    def home_file(self) -> str:
        """Return the home file from configuration.

        :return: Home file
        :rtype: str
        """
        return self._update_prm(self.PRM_HOME, constants.HOME_FILE)

    def exclude_files(self) -> List[str]:
        """Return the excluded files from configuration.

        :return: Excluded files
        :rtype: list[str]
        """
        return self._update_prm(self.PRM_EXCL_FILES,
                                ' '.join(constants.EXCLUDE_FILES)).split(' ')

    def exclude_dirs(self) -> List[str]:
        """Return the excluded dirs from configuration.

        :return: Excluded dirs
        :rtype: list[str]
        """
        return self._update_prm(self.PRM_EXCL_DIRS,
                                ' '.join(constants.EXCLUDE_DIRS)).split(' ')

    def plugins_html(self) -> List[str]:
        """Return the HTML plugins from configuration.

        :return: HTML Plugins to activate
        :rtype: list[str]
        """
        return self._update_prm(self.PRM_PLUGINS_HTML,
                                ' '.join(constants.PLUGINS_HTML)).split(' ')


# autoapi.sphinx directive
__api__ = [
    'Config',
]
