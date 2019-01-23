# Copyright (C) 2019  Collin Capano
# This program is free software; you can redistribute it and/or modify it
# under the terms of the GNU General Public License as published by the
# Free Software Foundation; either version 3 of the License, or (at your
# option) any later version.
#
# This program is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU General
# Public License for more details.
#
# You should have received a copy of the GNU General Public License along
# with this program; if not, write to the Free Software Foundation, Inc.,
# 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301, USA.

"""Arbitrary utilities used by multiple modules."""


def get_random_state(random_state):
    """Creates/passes a RandomState.

    Parameters
    ----------
    random_state : numpy.random.RandomState, int, or None
        If int or None, will create a new ``RandomState``, passing the int
        or None to it. If an int, this will be the seed of the new state.
        If the `random_state` is already a ``RandomState`` instance, this will
        just return that.

    Returns
    -------
    numpy.random.RandomState :
        The random state. If ``random_state`` was already ``RandomState``, just
        returns the same. Otherwise, the returned will be a new ``RandomState``
        instance.
    """
    if not isinstance(random_state, numpy.random.RandomState):
        random_state = numpy.random.RandomState(random_state)
    return random_state
