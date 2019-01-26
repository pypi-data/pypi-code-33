#    This file is part of qdpy.
#
#    qdpy is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Lesser General Public License as
#    published by the Free Software Foundation, either version 3 of
#    the License, or (at your option) any later version.
#
#    qdpy is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
#    GNU Lesser General Public License for more details.
#
#    You should have received a copy of the GNU Lesser General Public
#    License along with qdpy. If not, see <http://www.gnu.org/licenses/>.

"""Collection of test functions and benchmarks for QD algorithms"""

from math import cos, pi


def rastrigin_normalised(ind, a=10.):
    """Rastrigin test function, with inputs and outputs scaled to be between 0. and 1."""
    n = float(len(ind))
    ind_n = [-5.12 + x * (5.12 * 2.) for x in ind]
    return (a * n + sum(x * x - a * cos(2. * pi * x) for x in ind_n)) / (a * n + n * (5.12 * 5.12 + a)),


def illumination_rastrigin_normalised(ind, nb_features=2):
    """A simple test function for illumination tasks based on the Rastrigin function. """
    fitness = 1. - rastrigin_normalised(ind)[0]
    features = list(ind[:nb_features])
    return [[fitness], features]


# MODELINE "{{{1
# vim:expandtab:softtabstop=4:shiftwidth=4:fileencoding=utf-8
# vim:foldmethod=marker
