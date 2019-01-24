import tokenize
from typing import *

T = TypeVar("T")


def pairwise(itr: Iterable[T], first: T) -> Iterable[Tuple[T, T]]:
    memo = first
    for item in itr:
        yield memo, item
        memo = item


def get_comment(line: str) -> str:
    if line.startswith("/*") and line.endswith("*/"):
        return line[2:-2].strip()
    else:
        return ""


class LineParseError(Exception):
    pass


def parse_line(line: str) -> Tuple[str, str]:
    lines = iter([line.encode("utf-8")])

    def rdln(size: int = -1) -> bytes:
        try:
            return next(lines)
        except StopIteration:
            return b""

    tokens = list(tokenize.tokenize(rdln))
    if len(tokens) != 7:
        raise LineParseError(f"Wrong number of tokens: {len(tokens)}, {tokens}")
    encoding, key, eq, value, semi, newline, endmarker = tokens
    if encoding.type != tokenize.ENCODING:
        raise LineParseError("No encoding token")
    if key.type != tokenize.STRING:
        raise LineParseError("Key not string")
    if eq.type != tokenize.OP:
        raise LineParseError("= not op")
    if value.type != tokenize.STRING:
        raise LineParseError("Value not string")
    if semi.type != tokenize.OP:
        raise LineParseError("; not op")
    if newline.type != tokenize.NEWLINE:
        raise LineParseError("Expected newline")
    if endmarker.type != tokenize.ENDMARKER:
        raise LineParseError("Expected endmarker")
    if eq.string != "=":
        raise LineParseError("= not =")
    if semi.string != ";":
        raise LineParseError("; not ;")
    return key.string, value.string


def parse(source: str) -> Iterable[Tuple[str, str, str]]:
    lines = map(str.strip, source.splitlines(keepends=False))
    for prev, line in pairwise(lines, ""):
        comment = get_comment(prev)
        try:
            key, value = parse_line(line)
        except LineParseError:
            continue
        yield key, value, comment
