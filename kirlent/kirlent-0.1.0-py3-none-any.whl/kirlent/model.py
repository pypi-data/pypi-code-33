# Copyright (C) 2018 H. Turgut Uyar <uyar@tekir.org>
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

"""The module that contains the data representation."""

from pathlib import Path


PARTS_FILE = "parts.txt"


class ContentHierarchy:
    """A file system hierarchy for storing content."""

    def __init__(self, root):
        """Initialize this content hierarchy.

        :sig: (Path) -> None
        :param root: Root folder for the content.
        """
        self.root = root.absolute()  # sig: Path
        """Absolute path of root folder of this content hierarchy."""

    @property
    def units(self):
        """Content units in this hierarchy.

        :sig: () -> Dict[str, Unit]
        """
        return {p.name: Unit(p, root=self) for p in self.root.glob("*") if p.is_dir()}


class Unit:
    """A content unit."""

    def __init__(self, src, *, root):
        """Initialize this unit.

        :sig: (Path, ContentHierarchy) -> None
        :param src: Root folder for unit sources.
        :param root: Content hierarchy that contains this unit.
        """
        self.src = src.absolute()  # sig: Path
        """Absolute path of the root source folder of this unit."""

        self.root = root  # sig: ContentHierarchy
        """Content hierarchy that contains this unit."""

        self.parts = []  # sig: List[Unit]
        """Subunits that make up this unit."""

        parts_path = Path(self.src, PARTS_FILE)
        if parts_path.exists():
            with open(parts_path) as f:
                self.parts = [p.strip() for p in f.readlines()]

    @property
    def slug(self):
        """Short name of this unit.

        :sig: () -> str
        """
        return self.src.name

    def sources(self, *, medium, lang):
        """Get the paths of source items that make up this unit.

        :sig: (str, str) -> Sequence[Path]
        :param medium: Type of medium for which to get the sources
        :param lang: Language of content.
        :return: Source item paths.
        """
        if len(self.parts) > 0:
            for part in self.parts:
                unit = self.root.units.get(part)
                yield from unit.sources(medium=medium, lang=lang)
        else:
            if medium == "slides":
                yield Path(self.src, f"slides.{lang}.rst")
            else:
                raise NotImplementedError(
                    "Media other than slides haven't been implemented yet"
                )

    def sphinx_extras(self):
        """Get the extra features needed for Sphinx output.

        :sig: () -> List[str]
        :return: Sphinx extras.
        """
        return ["math"]
