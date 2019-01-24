from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path
from subprocess import check_call
from tempfile import TemporaryDirectory
from typing import *

import chardet

from .parser import parse

if TYPE_CHECKING:
    DirEntry = os.DirEntry[str]
else:
    DirEntry = os.DirEntry

PathFilter = Callable[[DirEntry], bool]


@dataclass(frozen=True, eq=True)
class LocalizableString:
    string: str
    comment: str


@dataclass
class LocalizableStrings:
    strings: Dict[str, LocalizableString]

    @classmethod
    def null(cls) -> LocalizableStrings:
        return cls({})

    @classmethod
    def from_source(cls, source: str) -> LocalizableStrings:
        return cls(
            {
                key: LocalizableString(string=value, comment=comment)
                for key, value, comment in parse(source)
            }
        )

    def to_source(self) -> str:
        lines = []
        for key, localized_string in sorted(self.strings.items()):
            if localized_string.comment:
                lines.append(f"/* {localized_string.comment} */")
            lines.append(f"{key} = {localized_string.string};")
            lines.append("")
        return "\n".join(lines)


def read_file(path: Path) -> Union[str, None]:
    if not path.exists():
        return None
    with path.open("rb") as fobj:
        data = fobj.read()
    candidates = ["utf-8"]
    encoding = chardet.detect(data)["encoding"]
    if encoding is not None:
        candidates.append(encoding)
    candidates.append("utf-16-le")
    for candidate in candidates:
        try:
            s: str = data.decode(candidate)
            return s
        except UnicodeDecodeError:
            continue
    return None


def read_strings(path: Path) -> LocalizableStrings:
    source = read_file(path)
    if source is None:
        return LocalizableStrings.null()
    return LocalizableStrings.from_source(source)


def scan_tree(path: Path, path_filter: PathFilter) -> Iterable[str]:
    for entry in os.scandir(path):
        if not path_filter(entry):
            continue
        if entry.is_file() and entry.name.endswith((".m", ".mm", ".swift")):
            yield entry.path
        elif entry.is_dir():
            yield from scan_tree(Path(entry.path), path_filter)


def generate_strings(
    sources: List[Path], path_filter: PathFilter
) -> LocalizableStrings:
    with TemporaryDirectory() as workspace:
        for src in sources:
            for entry in scan_tree(src, path_filter):
                check_call(
                    ["genstrings", "-a", "-littleEndian", "-o", workspace, entry]
                )
        return read_strings(Path(workspace) / "Localizable.strings")


def merge_strings(
    strings: LocalizableStrings, translations: LocalizableStrings
) -> LocalizableStrings:
    return LocalizableStrings(
        {
            key: translations.strings.get(key, value)
            for key, value in strings.strings.items()
        }
    )
