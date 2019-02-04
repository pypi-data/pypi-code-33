# Copyright (C) 2017-2018 H. Turgut Uyar <uyar@tekir.org>
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

"""The module that contains the command line interface for Kırlent."""

import sys
from argparse import ArgumentParser
from pathlib import Path

from . import __version__
from .tasks import TaskManager


DEFAULT_SRC_ROOT = Path("content")  # sig: Path
"""Default root folder for content sources."""


def make_parser(*, prog):
    """Build a parser for command line arguments.

    :sig: (str) -> ArgumentParser
    :param prog: Name of program.
    :return: Generated parser.
    """
    parser = ArgumentParser(prog=prog)
    parser.add_argument("--version", action="version", version="%(prog)s " + __version__)

    parser.add_argument("--src", help="root folder for content sources")
    parser.add_argument("--out", help="root folder for generated output")

    commands = parser.add_subparsers(metavar="command", dest="command")
    commands.required = True

    unit_parser = ArgumentParser(add_help=False)
    unit_parser.add_argument("units", nargs="?", help="pattern for units to process")

    rv_parser = commands.add_parser(
        "rv", help="generate HTML slides using RevealJS", parents=[unit_parser]
    )
    rv_parser.set_defaults(
        func=lambda m, a: m.run("generate_revealjs", pattern=a.units, exits=True)
    )

    dt_parser = commands.add_parser(
        "dt", help="generate PDF slides using Decktape", parents=[unit_parser]
    )
    dt_parser.set_defaults(
        func=lambda m, a: m.run("generate_decktape", pattern=a.units, exits=True)
    )

    clean_parser = commands.add_parser(
        "clean", help="clean build folders", parents=[unit_parser]
    )
    clean_parser.set_defaults(
        func=lambda m, a: m.run("clean_build_folders", pattern=a.units, exits=True)
    )

    task_parser = commands.add_parser("task", help="run specific task")
    task_parser.add_argument("name", help="task name")
    task_parser.set_defaults(func=lambda m, a: m.run(a.name, exits=True))

    return parser


def main(argv=None):
    """Start the command line interface.

    :sig: (Optional[List[str]]) -> None
    :param argv: Command line arguments.
    """
    parser = make_parser(prog="kirlent")

    argv_ = argv if argv is not None else sys.argv
    arguments = parser.parse_args(argv_[1:])

    cache_root = Path.home() / ".cache" / "kirlent"
    cache_root.mkdir(parents=True, exist_ok=True)

    tasks_db = cache_root / "tasks.db"

    src_root = Path(arguments.src) if arguments.src is not None else DEFAULT_SRC_ROOT
    out_root = Path(arguments.out) if arguments.out is not None else src_root.parent / "_build"
    task_manager = TaskManager(src_root, out_root, deps=tasks_db)

    # run the handler for the selected command
    try:
        arguments.func(task_manager, arguments)
    except RuntimeError as e:
        print(e, file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
