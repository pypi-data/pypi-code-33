#!/usr/bin/env python
# -*- coding: ascii -*-

r"""
IntroRL provides a framework for exploring Reinforcement Learning.
It uses the text book "Reinforcement Learning" by Sutton & Barto as a reference.

IntroRL includes models from Sutton & Barto and shows a number of worked solutions to the book's problems and examples.


IntroRL
Copyright (C) 2019  Charlie Taylor

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.

-----------------------

"""
import os
here = os.path.abspath(os.path.dirname(__file__))


# for multi-file projects see LICENSE file for authorship info
# for single file projects, insert following information
__author__ = 'Charlie Taylor'
__copyright__ = 'Copyright (c) 2018 Charlie Taylor'
__license__ = 'GPL-3'
exec( open(os.path.join( here,'_version.py' )).read() )  # creates local __version__ variable
__email__ = "cet@appliedpython.com"
__status__ = "3 - Alpha" # "3 - Alpha", "4 - Beta", "5 - Production/Stable"

#
# import statements here. (built-in first, then 3rd party, then yours)
#
# Code goes below.
# Adjust docstrings to suite your taste/requirements.
#

class Environment(object):
    """IntroRL provides a framework for exploring Reinforcement Learning.
    It uses the text book "Reinforcement Learning" by Sutton & Barto as a reference.

    This version is a place-holder for the full version.
    """

    def __init__(self):
        """Inits Environment """
        pass


if __name__ == '__main__':
    C = Environment()
