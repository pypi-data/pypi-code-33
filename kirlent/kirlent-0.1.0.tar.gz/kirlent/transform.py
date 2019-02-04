# Copyright (C) 2017-2019 H. Turgut Uyar <uyar@tekir.org>
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

"""The module that contains the markup transformations."""

from io import StringIO
from pathlib import Path

from .utils import relative_path


def generate_revealjs_sources(sources, target):
    """Combine a number of Kırlent sources and convert to a RevealJS file.

    :sig: (List[Path], Path) -> None
    :param sources: Paths of Kırlent source files.
    :param target: Path of target RevealJS file.
    """
    stream = StringIO()
    for source in sources:
        with source.open() as f:
            for line in f.readlines():
                if ".. image::" in line:
                    asset_path = line.split(".. image::")[1].strip()
                    full_path = Path(source.parent, asset_path)
                    rel_path = relative_path(full_path, target.parent)
                    line = line.replace(asset_path, str(rel_path))
                print(line, file=stream, end="")
        print("\n\n", file=stream)
    content = stream.getvalue()

    with target.open(mode="w") as f:
        f.write(content)
