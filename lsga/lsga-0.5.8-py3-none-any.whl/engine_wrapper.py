#!/usr/bin/env python
# -*- coding: utf-8 -*-

from lsga import GAEngine
from lsga.components import *
from lsga.operators import *
from lsga.analysis.fitness_store import FitnessStore
from lsga.analysis.console_output import ConsoleOutput


class EngineWrapper():

    def create_engine(self, ranges, n_jobs=1, eps=0.001, population_size=50, encoding='binary', selection='tournament',
                      crossover='uniform', mutation='flip_bit'):
        """

        :param ranges:
        :param n_jobs:
        :param eps:
        :param population_size:
        :param encoding:
        :param selection:
        :param crossover:
        :param mutation:
        """

        assert encoding in ['binary', 'decimal']
        assert selection in ['tournament', 'roulette_wheel', 'linear_ranking', 'exponential_ranking']
        assert crossover in ['uniform']
        assert mutation in ['flip_bit']

        if encoding == 'binary':
            indv_template = BinaryIndividual(ranges=ranges, eps=eps)
        else:
            indv_template = BinaryIndividual(ranges=ranges, eps=eps)

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
