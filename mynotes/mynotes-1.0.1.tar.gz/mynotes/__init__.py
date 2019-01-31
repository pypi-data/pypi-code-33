"""mynotes package entry."""

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

from .gen import build_index, generate_html
from .utils import Params
from .config import Config
from .constants import VERSION, PACKAGE_NAME

NAME = PACKAGE_NAME

__all__ = ['VERSION',
           'NAME',
           'Params',
           'Config',
           'build_index',
           'generate_html']
