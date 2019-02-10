#!/usr/bin/env python
# -*- coding: utf-8 -*-

from lsga import GAEngine
from lsga.components import *
from lsga.operators import *
from lsga.analysis.fitness_store import FitnessStore
from lsga.analysis.console_output import ConsoleOutput

import sys, inspect


class EngineWrapper():

    def create_engine(self, ranges, n_jobs=1, eps=0.001, population_size=50, encoding='binary', selection='tournament',
                      crossover='uniform', mutation='flip_bit'):
        """

        :param ranges: value ranges for all entries in solution.
        :type ranges: tuple list
        :param n_jobs: The maximum number of parallel training procedures.
            - If ``-1``, all CPUs are used.
            - If ``1`` is given, no parallel computing code is used at all,\
                which is useful for debugging.
            - For ``n_jobs`` below ``-1``, ``(n_cpus + n_jobs + 1)`` are\
                used.  For example, with ``n_jobs = -2`` all CPUs but one are\
                used.
            Default is ``1``.
        :type n_jobs: int

        :param eps: the decrete precision of binary sequence
        :type eps: float

        :param population_size: The size of population, number of individuals in population.
        :type population_size: int

        :param encoding: The type of encoding to be used for chromosome encoding.
        :type encoding: string  ['binary', 'decimal']

        :param selection: The Selection to be used for individual seleciton.
        :type selection: string ['tournament', 'roulette_wheel', 'linear_ranking', 'exponential_ranking']

        :param crossover: The Crossover to be used for individual crossover.
        :type crossover: string ['uniform']

        :param mutation: The Mutation to be used for individual mutation.
        :type mutation: string ['flip_bit']
        """

        assert encoding in ['binary', 'decimal']
        assert selection in ['tournament', 'roulette_wheel', 'linear_ranking', 'exponential_ranking']
        assert crossover in ['uniform']
        assert mutation in ['flip_bit']

        if encoding == 'binary':
            indv_template = BinaryIndividual(ranges=ranges, eps=eps)
        else:
            indv_template = DecimalIndividual(ranges=ranges, eps=eps)

        if selection == 'tournament':
            lsga_selection = TournamentSelection()
        elif selection == 'roulette_wheel':
            lsga_selection = RouletteWheelSelection()
        elif selection == 'linear_ranking':
            lsga_selection = LinearRankingSelection()
        else:
            lsga_selection = ExponentialRankingSelection()

        if crossover == 'uniform':
            lsga_crossover = UniformCrossover(pc=0.8, pe=0.5)

        if mutation == 'flip_bit':
            lsga_mutation = FlipBitBigMutation(pm=0.1, pbm=0.55, alpha=0.6)

        population = Population(indv_template=indv_template, size=population_size, n_jobs=n_jobs).init()

        engine = GAEngine(population=population, selection=lsga_selection,
                          crossover=lsga_crossover, mutation=lsga_mutation,
                          analysis=[ConsoleOutput, FitnessStore])

        return engine

    def print_classes(self):
        for name, obj in inspect.getmembers(sys.modules[__name__]):
            if inspect.isclass(obj):
                print(obj)