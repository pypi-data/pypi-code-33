#!/usr/bin/env python
# -*- coding: utf-8 -*-

''' Flip Bit mutation implementation. '''

from random import random, uniform

from ...mpiutil import MPIUtil
from ...plugin_interfaces.operators.mutation import Mutation
from ...components.binary_individual import BinaryIndividual
from ...components.decimal_individual import DecimalIndividual

mpi = MPIUtil()


class FlipBitMutation(Mutation):
    ''' Mutation operator with Flip Bit mutation implementation.

    :param pm: The probability of mutation (usually between 0.001 ~ 0.1)
    :type pm: float in range (0.0, 1.0]
    '''
    def __init__(self, pm):
        if pm <= 0.0 or pm > 1.0:
            raise ValueError('Invalid mutation probability')

        self.pm = pm

    def mutate(self, individual, engine):
        ''' Mutate the individual.

        :param individual: The individual on which crossover operation occurs
        :type individual: :obj:`lsga.components.IndividualBase`

        :param engine: Current genetic algorithm engine
        :type engine: :obj:`lsga.engine.GAEngine`

        :return: A mutated individual
        :rtype: :obj:`lsga.components.IndividualBase`
        '''
        do_mutation = True if random() <= self.pm else False

        if do_mutation:
            for i, genome in enumerate(individual.chromsome):
                no_flip = True if random() > self.pm else False
                if no_flip:
                    continue

                if type(individual) is BinaryIndividual:
                    individual.chromsome[i] = genome^1
                elif type(individual) is DecimalIndividual:
                    a, b = individual.ranges[i]
                    eps = individual.precisions[i]
                    n_intervals = (b - a)//eps
                    n = int(uniform(0, n_intervals + 1))
                    individual.chromsome[i] = a + n*eps
                else:
                    raise TypeError('Wrong individual type: {}'.format(type(individual)))

            # Update solution.
            individual.solution = individual.decode()

        return individual