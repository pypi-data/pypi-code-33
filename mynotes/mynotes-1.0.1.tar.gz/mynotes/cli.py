"""Client UI."""

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

import argparse
import mynotes
import sys


def _parser_args(description: str) -> argparse.Namespace:
    """Manage arguments.

    :param str description: Description of the program
    :return: Arguments
    :rtype: argparse.Namespace
    """
    parser = argparse.ArgumentParser(
        formatter_class=argparse.RawDescriptionHelpFormatter,
        description=description +
        '\n\n'
        f'version {mynotes.VERSION}\n'
        '\n'
        'Copyright (C) 2018 Yorick Brunet\n'
        'This program comes with ABSOLUTELY NO WARRANTY.\n'
        'This is free software, and you are welcome to redistribute it\n'
        'under the terms of the GNU General Public License as published by\n'
        'the Free Software Foundation, either version 3 of the License, or\n'
        'any later version.'
        )

    parser.add_argument('--verbose', '-v',
                        dest='verbose',
                        action='store_true',
                        help='Increase verbosity')
    parser.add_argument('--config', '-c',
                        dest='config',
                        default=mynotes.constants.CONFIG_FILE,
                        help='Configuration file')
    parser.add_argument('--version', '-V',
                        dest='version',
                        action='store_true',
                        help='Show version information')

    args = parser.parse_args()

    if args.version:
        print(mynotes.VERSION)
        sys.exit(0)

    return args


def build_index():
    """Build index files for notes tree.

    The tree is "walked" and an index file is created inside every directory
    with links to files and inner directories.

    This script can be configured using the configuration file.
    """
    args = _parser_args('Build index files for notes tree.')

    cfg = mynotes.config.Config(args.config)

    if args.verbose:
        print(f'Index file ...... {cfg.index_file()}')
        print(f'Home file ....... {cfg.home_file()}')
        print(f'Excluded dirs ... {", ".join(cfg.exclude_dirs())}')
        print(f'Excluded files .. {", ".join(cfg.exclude_files())}')
        print()

    prms = mynotes.Params(
        cfg.index_file(),
        cfg.home_file(),
        cfg.markdown_ext(),
        cfg.exclude_dirs(),
        cfg.exclude_files(),
        args.verbose)
    mynotes.gen.build_index('.', prms)


def generate_html():
    """Build HTML files for notes tree.

    The tree is "walked" and an HTML file is created for each Markdown file
    in a separate directory.

    This script can be configured using the configuration file.
    """
    args = _parser_args('Generate HTML files for markdown files.')

    cfg = mynotes.config.Config(args.config)

    if args.verbose:
        print(f'Index file ...... {cfg.index_file()}')
        print(f'Home file ....... {cfg.home_file()}')
        print(f'Markdown ext .... {cfg.markdown_ext()}')
        print(f'Excluded dirs ... {", ".join(cfg.exclude_dirs())}')
        print(f'Excluded files .. {", ".join(cfg.exclude_files())}')
        print(f'Plugins ......... {", ".join(cfg.plugins_html())}')
        print()

    prms = mynotes.Params(
        cfg.index_file(),
        cfg.home_file(),
        cfg.markdown_ext(),
        cfg.exclude_dirs(),
        cfg.exclude_files(),
        args.verbose)
    mynotes.gen.generate_html('.', prms, cfg.plugins_html())


# autoapi.sphinx directive
__api__ = [
    '_parser_args',
    'build_index',
    'generate_html',
]
