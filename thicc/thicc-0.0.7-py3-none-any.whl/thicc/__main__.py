import argparse
import sys

from . import __version__
from .thicc import map_string


def get_args(args=None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Convert characters to their fullwidth representation if one exists."
    )
    parser.add_argument(
        "-r",
        "--reverse",
        action="store_true",
        help="Instead, convert characters to their regular representation.",
    )
    parser.add_argument(
        "-v", "--version", action="version", version=f"%(prog)s {__version__}"
    )
    parser.add_argument(
        "file",
        nargs="?",
        type=argparse.FileType(mode="rb", encoding="utf8"),
        default=sys.stdin,
        metavar="filename",
        help="The file to convert. If omitted, standard input is read instead.",
    )
    args = parser.parse_args(args)
    return args


def main():
    args = get_args()
    for line in args.file:
        sys.stdout.write(map_string(line, reverse=args.reverse))
    if sys.stdout.isatty():
        sys.stdout.write("\n")


if __name__ == "__main__":
    main()
