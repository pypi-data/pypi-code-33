# Copyright (C) 2017 H. Turgut Uyar <uyar@tekir.org>
#
# This file is part of Kırlent.
#
# Kırlent is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Kırlent is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Kırlent.  If not, see <http://www.gnu.org/licenses/>.

"""The module that contains various utility functions."""

from itertools import dropwhile, zip_longest
from pathlib import Path


def relative_path(src, dst):
    """Get the relative path of a file starting from a destination folder.

    :sig: (Path, Path) -> Path
    :param src: Path of source file to find the relative path for.
    :param dst: Path of destination folder to start the relative path from.
    :return: Relative path from start to source file.
    """
    parts = zip_longest(src.absolute().parts, dst.absolute().parts)
    path_diff = dropwhile(lambda ps: ps[0] == ps[1], parts)
    down_parts, up_parts = zip(*path_diff)
    up_path = Path(*[".." for p in up_parts if p is not None])
    down_path = Path(*[p for p in down_parts if p is not None])
    return up_path / down_path
