# -*- coding: utf-8 -*-
#
# Copyright 2018 Barry Muldrey
#
# This file is part of waverunner.
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, see <http://www.gnu.org/licenses/>.

__version__ = "0.2b3"            # this is the definitive version for distribution
__author__ = "Barry Muldrey"
__copyright__ = "Copyright 2018"
__license__ = "GNU Affero GPL"
__maintainer__ = "Barry Muldrey"
__email__ = "barry@muldrey.net"
__status__ = "Alpha"
__credits__ = []


from .Server import Waverunner
from .Server import PublicMethod, SecureMethod
# from .Server import PublicInstance, SecureInstance
from .Server import external_request


def secure(item):
    if callable(item):
        return SecureMethod(item)
    # else:
    #     return SecureInstance(item)


def insecure(item):
    if callable(item):
        return PublicMethod(item)
    # else:
    #     return PublicInstance(item)


