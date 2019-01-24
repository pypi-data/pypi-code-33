from __future__ import annotations

import fnmatch
import os
from dataclasses import dataclass
from pathlib import Path
from typing import *

import click
import toml

from pygenstrings.genstrings import (
    generate_strings,
    read_strings,
    merge_strings,
    PathFilter,
)


class ConfigError(Exception):
    pass


T = TypeVar("T")


@dataclass
class Box(Generic[T]):
    """
    https://github.com/python/mypy/issues/5485 workaround
    """

    inner: T

    def unbox(self) -> T:
        return self.inner


@dataclass
class Config:
    sources: List[Path]
    destination: Path
    languages: List[str]
    path_filter: Box[PathFilter]

    @classmethod
    def merge(
        cls,
        sources: List[str],
        destination: Optional[str],
        languages: List[str],
        exclude: List[str],
        config: Optional[Dict[str, Any]],
    ) -> Config:
        if config:
            if not sources:
                sources = config.get("sources", [])
            if not destination:
                destination = config.get("destination", None)
            if not languages:
                languages = config.get("languages", [])
            if not exclude:
                exclude = config.get("exclude", [])
        if not sources:
            raise ConfigError("Must define at least one source")
        source_paths = [Path(src) for src in sources]
        if not all(src.exists() for src in source_paths):
            raise ConfigError("Not all sources exist")
        if destination is None:
            dest_path = Path.cwd()
        else:
            dest_path = Path(destination)
        if not dest_path.exists():
            raise ConfigError("Destination does not exist")
        if not dest_path.is_dir():
            raise ConfigError("Destination is not a directory")
        if not languages:
            raise ConfigError("Must specify at least one language")
        if exclude:
            path_filter = make_filter(exclude)
        else:
            path_filter = null_filter
        return cls(
            sources=source_paths,
            destination=dest_path,
            languages=languages,
            path_filter=Box(path_filter),
        )


def null_filter(entry: os.DirEntry[str]) -> bool:
    return True


def make_filter(exclude: List[str]) -> PathFilter:
    def fltr(entry: os.DirEntry[str]) -> bool:
        for pat in exclude:
            if fnmatch.fnmatch(entry.path, f"*{pat}"):
                return False
        return True

    return fltr


def find_translations(path: Path, langs: Iterable[str]) -> Iterable[Path]:
    for lang in langs:
        directory = path / f"{lang}.lproj"
        if not directory.exists():
            directory.mkdir()
        yield directory / "Localizable.strings"


def read_config(config_file: Optional[TextIO]) -> Optional[Dict[str, Any]]:
    if config_file:
        return toml.load(config_file).get("pygenstrings", {})
    path = Path.cwd() / "pygenstrings.toml"
    if path.exists() and path.is_file():
        with path.open("r") as fobj:
            return toml.load(fobj).get("pygenstrings", {})
    path = Path.cwd() / "pyproject.toml"
    if path.exists() and path.is_file():
        with path.open("r") as fobj:
            tools = toml.load(fobj).get("tool", {})
            assert isinstance(tools, dict)
            return tools.get("pygenstrings", {})
    return None


@click.command()
@click.option(
    "-s",
    "--src",
    type=click.Path(dir_okay=True, file_okay=False, exists=True),
    multiple=True,
)
@click.option(
    "-d", "--dst", type=click.Path(dir_okay=True, file_okay=False, exists=True)
)
@click.option("-l", "--lang", multiple=True)
@click.option("-e", "--exclude", multiple=True)
@click.option("-c", "--config-file", type=click.File(mode="r"))
def main(
    src: List[str],
    dst: Optional[str],
    lang: List[str],
    exclude: List[str],
    config_file: Optional[TextIO],
) -> None:
    config = Config.merge(
        sources=src,
        destination=dst,
        languages=lang,
        exclude=exclude,
        config=read_config(config_file),
    )
    strings = generate_strings(config.sources, config.path_filter.unbox())
    click.echo(f"Found {len(strings.strings)} strings to translate")
    for path, language in zip(
        find_translations(config.destination, config.languages), config.languages
    ):
        translation = read_strings(path)
        result = merge_strings(strings, translation)
        with path.open("w", encoding="utf-8") as fobj:
            fobj.write(result.to_source())
        click.echo(f"Wrote {language}")
    click.echo("Done")
