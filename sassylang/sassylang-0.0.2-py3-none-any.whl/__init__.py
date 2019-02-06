#Copyright 2018 Jonathan Sacramento

#This file is part of sassy.
#
#sassy is free software: you can redistribute it and/or modify
#it under the terms of the GNU General Public License as published by
#the Free Software Foundation, either version 3 of the License, or
#(at your option) any later version.
#
#sassy is distributed in the hope that it will be useful,
#but WITHOUT ANY WARRANTY; without even the implied warranty of
#MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#GNU General Public License for more details.
#
#You should have received a copy of the GNU General Public License
#along with sassy. If not, see <http://www.gnu.org/licenses/>.

import docopt
import fileinput

from .interpreter import Interpreter

__version__ = '0.0.2'

__doc__ = """sassy - interpreter for the sassy macro language

Usage:
    sassy [-i | --ignore] [<file>...]
    sassy (-h | --help)
    sassy (-v | --version)

Options:
    -i, --ignore        Ignore whitespace outside of macro tags
    -h, --help          Show help description.
    -v, --version       Show version.
"""


def main():
    # needs to be outside of try block to let docopt handle bad input
    arguments = docopt.docopt(__doc__, version='sassy v' + __version__)

    try:
        Interpreter(arguments).process_input(fileinput)
    except FileNotFoundError:
        print('File not found!')


if __name__ == '__main__':
    main()
