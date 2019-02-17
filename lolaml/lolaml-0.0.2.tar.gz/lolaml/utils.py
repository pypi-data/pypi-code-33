from pathlib import Path
from typing import List


def lprint(text: str) -> None:
    print(f"# LOLA: {text}")


def ls(path: str) -> List[Path]:
    """Return a list of content under `path`."""
    return [p for p in Path(path).rglob("*")]


def ls_files(path: str) -> List[Path]:
    """Return a list of all files under `path`."""
    return [p for p in Path(path).rglob("*") if p.is_file()]
