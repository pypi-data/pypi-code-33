"""Plugins for HTML generation."""

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

import os.path
from typing import List

from .utils import Params
from . import constants as constants


def _toc(prms: Params,
         file_: str,
         md: str,
         ) -> str:
    """Generate TOC from markdown data.

    :param Params prms: Parameters
    :param str file_: File name
    :param str md: Markdown data
    :return: Modified Markdown data including TOC
    :rtype: str
    """
    if file_ == prms.index:
        return md
    else:
        toc = '**TOC**\n\n'
        count = 0
        # Find all headings
        headers = constants.RE_ANCHOR.findall(md)
        # For each heading, add anchor to HTML data
        for full, level, text in headers:
            md = md.replace(full,
                            f'{level} <a name="anchor{count}"/>{text}')
            toc += '\t'*(len(level)-1) + f'* [{text}](#anchor{count})\n'
            count += 1
        toc += '\n'
        return toc + md


def _links_index(prms: Params,
                 file_: str,
                 root: str,
                 md: str,
                 ) -> str:
    """Generate links to upper/top index.

    :param Params prms: Parameters
    :param str file_: File name
    :param str root: Root path
    :param str md: Markdown data
    :return: Modified Markdown data with links to upper/top index
    :rtype: str
    """
    def path_index_up() -> str:
        """Create path to go to the upper index.

        :return: Path
        :rtype: str
        """
        return os.path.join('..', prms.index)

    def path_index_top() -> str:
        """Create path to go to the top index.

        :return: Path
        :rtype: str
        """
        def one_level(n: int) -> str:
            if n > 1:
                return os.path.join('..', one_level(n-1))
            else:
                return '..'
        return os.path.join(one_level(len(root.split('/'))-1),
                            prms.index)

    # Include in each index file: back to top/up
    if file_ == prms.index:
        if root != '.':
            return f'[Up]({path_index_up()})' + \
                   ' - ' + \
                   f'[Top]({path_index_top()})\n\n' + \
                   md
        else:
            return md
    # Include in each non-index file: back to index
    else:
        return f'[Up]({prms.index})\n\n' + md


def generate_plugins_data(prms: Params,
                          li: List[str],
                          file_: str,
                          root: str,
                          md: str,
                          ) -> str:
    """Generate data from plugins.

    :param Params prms: Parameters
    :param list[str] li: List of plugins to use
    :param str file_: File name
    :param str root: Root path
    :param str md: Markdown data
    :return: Modified Markdown data
    :rtype: str
    """
    # Generate TOC
    if constants.PLUGIN_HTML_TOC in li:
        md = _toc(prms, file_, md)
    # Generate links to upper/top index
    if constants.PLUGIN_HTML_LINKS_INDEX in li:
        md = _links_index(prms, file_, root, md)
    return md


# autoapi.sphinx directive
__api__ = [
    '_toc',
    '_links_index',
    'generate_plugins_data',
]
