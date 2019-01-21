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

"""Basic operators and tools used to design QD or evoluationary algorithms."""

import numpy as np
import random
from typing import Sequence, Callable, Tuple
from itertools import repeat

from qdpy.base import *


########### SELECTION ########### {{{1

def sel_random(collection: Sequence[Any]):
    """Select and return one individual at random among `collection`.

    Parameters
    ----------
    :param collection: Sequence[Any]
        The individuals to select from.
    """
    return random.choice(collection)



########### MUTATIONS ########### {{{1

def mut_gaussian(individual: T, mu: float, sigma: float, mut_pb: float) -> T:
    """Return a gaussian mutation of mean `mu` and standard deviation `sigma`
    on selected items of `individual`. `mut_pb` is the probability for each
    item of `individual` to be mutated.
    Mutations are applied directly on `individual`, which is then returned.

    Parameters
    ----------
    :param individual
        The individual to mutate.
    :param mu: float
        The mean of the gaussian mutation.
    :param sigma: float
        The standard deviation of the gaussian mutation.
    :param mut_pb: float
        The probability for each item of `individual` to be mutated.
    """
    for i in range(len(individual)):
        if random.random() < mut_pb:
            individual[i] += random.gauss(mu, sigma)
    return individual



def mut_polynomial_bounded(individual: T, eta: float, low: float, up: float, mut_pb: float) -> T:
    """Return a polynomial bounded mutation, as defined in the original NSGA-II paper by Deb et al.
    Mutations are applied directly on `individual`, which is then returned.
    Inspired from code from the DEAP library (https://github.com/DEAP/deap/blob/master/deap/tools/mutation.py).

    Parameters
    ----------
    :param individual
        The individual to mutate.
    :param eta: float
        Crowding degree of the mutation.
        A high ETA will produce mutants close to its parent,
        a small ETA will produce offspring with more differences.
    :param low: float
        Lower bound of the search domain.
    :param up: float
        Upper bound of the search domain.
    :param mut_pb: float
        The probability for each item of `individual` to be mutated.
    """
    for i in range(len(individual)):
        if random.random() < mut_pb:
            x = individual[i]
            delta_1 = (x - low) / (up - low)
            delta_2 = (up - x) / (up - low)
            rand = random.random()
            mut_pow = 1. / (eta + 1.)

            if rand < 0.5:
                xy = 1. - delta_1
                val = 2. * rand + (1. - 2. * rand) * xy**(eta + 1.)
                delta_q = val**mut_pow - 1.
            else:
                xy = 1. - delta_2
                val = 2. * (1. - rand) + 2. * (rand - 0.5) * xy**(eta + 1.)
                delta_q = 1. - val**mut_pow

            x += delta_q * (up - low)
            x = min(max(x, low), up)
            individual[i] = x
    return individual




########### COMBINED OPERATORS ########### {{{1

def sel_or_init(collection: Sequence[Any], sel_fn: Callable, sel_pb: float,
        init_fn: Callable, init_pb: float = 0., return_flag: bool = True):
    """Either select an individual from `collection` by using function `sel_pb`,
    or initialise a new individual by using function `init_pb`.
    If `collection` is empty, it will always initialise a new individual, not perform selection.

    Parameters
    ----------
    :param collection: Sequence[Any]
        The individuals to select from.
    :param sel_fn: Callable
        The selection function.
    :param sel_pb: float
        The probability of performing selection.
    :param init_fn: Callable
        The initialisation function.
    :param init_pb: float
        The probability of performing initialisation.
    :param return_flag: bool
        If set to True, the function will return a Tuple[IndividualLike, bool] with a first item corresponding
        to the selected or initialised individual, and the second item a flag set to True if the first item
        was selected, and set to False if it was initialised.
        If set to False, the function will return the selected or initialised IndividualLike.
    """
    def ret(res, f):
        return (res, f) if return_flag else res
    if len(collection) == 0:
        return ret(init_fn(), False)
    operation = np.random.choice(range(2), p=[sel_pb, init_pb])
    if operation == 0: # Selection
        return ret(sel_fn(collection), True)
    else: # Initialisation
        return ret(init_fn(), False)


def mut_or_cx(individuals: Union[IndividualLike, Sequence[IndividualLike]],
        mut_fn: Callable, cx_fn: Callable) -> Sequence[IndividualLike]:
    """Either perform a mutation (using function `mut_fn`) or a crossover (using function `cx_fn`)
    depending on the nature and length of `individuals`.
    If `individuals` is an IndividualLike or a Sequence of one IndividualLike, a mutation will be performed.
    If `individuals` is a Sequence of two IndividualLike, a crossover will be performed.

    Parameters
    ----------
    :param individuals: Union[IndividualLike, Sequence[IndividualLike]]
        The individual(s) to mutate or crossover.
    :param mut_fn: Callable
        The mutation function.
    :param cx_fn: Callable
        The crossover function.

    Return
    ------
    The resulting individual(s).
    """
    if isinstance(individuals, IndividualLike):
        return [mut_fn(individuals)]
    elif isinstance(individuals, Sequence) and len(individuals) == 1:
        return [mut_fn(individuals[0])]
    elif isinstance(individuals, Sequence) and len(individuals) > 1:
        return cx_fn(individuals)


# MODELINE	"{{{1
# vim:expandtab:softtabstop=4:shiftwidth=4:fileencoding=utf-8
# vim:foldmethod=marker
