__author__ = "Trey Guest"
__license__ = "GNU"
__version__ = "1.0.0"
__maintainer__ = "Trey Guest"
__email__ = "twguest@students.latrobe.edu.au"
__status__ = "Production"

#    Chromosome is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Lesser General Public License as
#    published by the Free Software Foundation, either version 3 of
#    the License, or (at your option) any later version.
#
#    Chromosome is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
#    GNU Lesser General Public License for more details.
#
#    You should have received a copy of the GNU Lesser General Public
#    License along with Chromosome. If not, see <http://www.gnu.org/licenses/>.

import sys
import numpy as np
import pandas as pd
import random
import datetime

from utils.progress import progress
from utils.selection_utils import Tournament

from fitness.euclid import Euclid, euclid, euclid_sn
from fitness.cosine import Cosine, cosine, cosine_sn
from fitness.dice import Dice, dice, dice_sn

from breed.npoint import Onepoint, Npoint
from breed.rand_choice import rnd_best

from selection.linrank import LinRank
from selection.rws import RoulletteWheelSelection
from selection.best import Best
from selection.tos import TournamentSelection
from selection.sus import StochasticUniversalSampling

from mutation.rnd_mutation import rnd_mutation

class Genome:

    """
    The genome object carries all genetic information for the target and seed
    matrices over any number of generations. All operations act on genome to
    progress the evolution of the population
    """


    def __init__(self, target, pop, nseeds, function, fitness = None):

        """
        :param target: target matrix object (as defined by target class)
        :param pop: optimal population size
        :param nseeds: the number of individuals generated in initio
        :param function: the transformation applied to the input matrix matrix
        :param fitness: global fitness function
        """

        self.generation = 0
        self.pop = pop # size of population
        self.nseeds = nseeds

        self.target = target
        # Here we inheret some params from the target class
        self.x = target.x
        self.y = target.y
        self.seed_dim = target.seed_dim

        if self.seed_dim == 3:
            self.z = target.z
        else:
            pass

        self.val_rng = target.val_rng
        self.val_max = target.val_max
        self.val_min = target.val_min
        self.decimals = target.decimals
        self.output = target.target

        self.function = function
        self.startTime = datetime.datetime.now()

        self.mode = ""
        self.time = 0

        self.population = []
        self.strongest = []
        self.cost = []
        self.strongest_gene = []
        self.processes = 0

        self.fitness = ""

        if fitness == None:
            self.fitness = euclid
        elif fitness == "euclid":
            self.fitness = euclid
            self.fitness_test = euclid_sn
        elif fitness == "cosine":
            self.fitness = cosine
            self.fitness_test = cosine_sn
        elif fitness == "dice":
            self.fitness = dice
            self.fitness_test = dice_sn


        # LOGGING
        self.stats_generation = []
        self.stats_strongest = []
        self.stats_winner = []
        self.stats_cost = []
        self.stats_ancestors = []
        self.stats_processes = []
        self.stats_time = []

################################################################################

    def init_population(self):

        """
        Population initialisation function

        ### Future Work should support smart population seeding - @twguest

        """

        if self.seed_dim == 3:
            x = self.x
            y = self.y
            z = self.z

            self.population = []

            i = 0

            while i in range(self.nseeds):
                if i % 5 == 0:
                    print(("Initialising Population Member {} of {}".format(i, self.nseeds)))
                self.population.append(np.round(np.random.uniform(self.val_min, self.val_max, [x,y,z]), self.decimals))
                i+=1

        elif self.seed_dim == 2:
            x = self.x
            y = self.y

            self.population = []

            i = 0

            while i in range(self.nseeds):
                if i % 5 == 0:
                    print(("Initialising Population Member {} of {}".format(i, self.nseeds)))
                self.population.append(np.round(np.random.uniform(self.val_min, self.val_max, [x,y]), self.decimals))
                i+=1

        print("************ Population Initialised")

        return self.population


################################################################################

    def display(self):

        """
        Display Utility: Flavour as neccesary
        """

        timeDiff = datetime.datetime.now() - self.startTime
        self.time = timeDiff.total_seconds()
        print(("{}\t{}\t{}".format(self.generation, self.strongest, timeDiff)))

################################################################################

    def linrank(self, pressure = None):

        """
        Wrapper function for Linrank
        """

        if pressure == None:
            pressure = 1

        LinRank(self)

    def RWS(self):

        """
        Wrapper function for RoulletteWheelSelection
        """

        RoulletteWheelSelection(self)

    def best(self):

        """
        Wrapper function for Best selection
        """

        Best(self)

    def TS(self, n = None):

        """
        Wrapper function for Tournament Selection
        """

        if n == None:
            n = np.ceil(int(self.pop/10))

        TournamentSelection(self, n)

    def SUS(self):

        """
        Wrapper Function for Stochastic Universal Sampling
        """

        StochasticUniversalSampling(self)

###############################################################################

    def onepoint(self, nchildren = None):

        """
        Onepoint Crossover Breeding
        : param nchildren: average number of children per individual (eff itr.)
        """

        if nchildren == None:
            nchildren = 1

        while len(self.population) < self.pop+self.pop*nchildren:
            self.population.append(Onepoint(self))

        progress(self)

        return self.population

    def npoint(self, N = None, nchildren = None):

        """ Npoint Crossover Breeding
        : param N: number of crossover points/slices
        : param nchildren: average number of children per individual (eff itr.)
        """

        if N == None:
            N = 2

        if nchildren == None:
            nchildren = 1


        while len(self.population) < self.pop+self.pop*nchildren:
            self.population.append(Npoint(self, N))

        progress(self)

        return self.population

    def rndbest(self, nI = None, nchildren = None):

        """
        A random crossover mechanism for the best N individuals
        : param nI: number of individuals
        : param nchildren: average number of children per individual (eff itr.)
        """
        if nchildren == None:
            nchildren = 1

        while len(self.population) < self.pop + self.pop*nchildren:
            self.population.append(rnd_best(self, nI))

        progress(self)
        return self.population


###############################################################################

    def random_mutation(self, nM = None, nI = None):

        """
        A random mutation function for generating nM mutations in nI
        individuals
        :param nM: number of mutations
        :param nI: number of individuals
        """

        if nM == None:
            nM = 1
        if nI == None:
            nI = 1

        itr = 0
        while itr < nI:
            rnd_mutation(self, nM)
            itr +=1

###############################################################################

if __name__ == "__main__":
    pass
