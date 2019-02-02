#!/usr/bin/env python

"""
Flavour selection.
"""

import sys

import numpy as np

from pyrqa.exceptions import SelectorNotFullySetupException, \
    NoFlavorException

__author__ = "Tobias Rawald"
__copyright__ = "Copyright 2015, 2018 The PyRQA project"
__credits__ = ["Tobias Rawald",
               "Mike Sips"]
__license__ = "Apache-2.0"
__maintainer__ = "Tobias Rawald"
__email__ = "pyrqa@gmx.net"
__status__ = "Development"


class Selector(object):
    """
    Selector base class.

    :ivar settings: Settings.
    :ivar opencl: OpenCL environment.
    :ivar device: Compute device, for which the flavour selection is conducted.
    :ivar variants: Pool of implementation variants that are the basis for flavour creation.
    """

    class Flavour(object):
        """
        A flavour is the comvination of a variant and a set of tuning parameter assignments.

        :ivar variant_instance: Concrete instance of variant including a set of tuning parameter assignments.
        :ivar _total_runtime: Total runtime for executing the flavour.
        :ivar _sub_matrix_count: Number of sub matrices that have been processed using the flavour.
        """

        def __init__(self,
                     variant_instance):
            self.variant_instance = variant_instance

            self._total_runtime = 0
            self._sub_matrix_count = 0

        @property
        def identifier(self):
            """
            Flavor identifier.

            :rtype: String.
            """

            return "%s%r%d" % (self.variant_instance.__class__.__name__,
                               self.variant_instance.optimisations_enabled,
                               self.variant_instance.loop_unroll)

        def update_runtimes(self,
                            sub_matrix,
                            runtimes):
            """
            Update the flavor runtimes regarding a specific sub matrix.
            NOTE: The runtimes are normalised to sub matrices containing 10^8 matrix elements for the purpose of comparability.

            :param sub_matrix: Sub matrix processed.
            :param runtimes: Runtimes for processing the sub matrix.
            :return:
            """
            self._total_runtime += runtimes.total * np.float32(np.power(10, 8)) / sub_matrix.elements
            self._sub_matrix_count += 1

        @property
        def average_total_runtime(self):
            """
            Average total runtime for processing all sub matrices using the flavor.

            :rtype: Floating point number.

            """

            if self._sub_matrix_count > 0:
                return self._total_runtime / self._sub_matrix_count

            return np.finfo(np.float32).max

    def __init__(self,
                 loop_unroll_factors):
        self.loop_unroll_factors = loop_unroll_factors

        self.is_setup = False

        self.settings = None
        self.device = None
        self.opencl = None
        self.variants = None
        self.variants_kwargs = None

        self.sub_matrix_count = 0

    def setup(self,
              device,
              settings,
              opencl,
              variants,
              variants_kwargs):
        """
        Setup the data regarding flavour creation.

        :param opencl: OpenCL environment.
        :param device: OpenCL device.
        :param variants: Variants.
        :param variants_kwargs: Variants keyword arguments.
        """

        self.settings = settings
        self.device = device
        self.opencl = opencl
        self.variants = variants
        self.variants_kwargs = variants_kwargs

        self.is_setup = True

    def increment_sub_matrix_count(self):
        """
        Increment the total number of sub matrices processed.
        """

        self.sub_matrix_count += 1

    def get_flavour(self):
        """
        Get flavour for processing the next sub matrix.
        """

        pass


class SingleSelector(Selector):
    """
    The same flavour is selected for processing all sub matrices.

    :ivar flavour: Single flavour.
    """

    def __init__(self,
                 loop_unroll_factors=(1, 2, 4, 8, 16, 32)):
        Selector.__init__(self,
                          loop_unroll_factors)

        self.flavour = None

    def get_flavour(self):
        """
        The first flavour created is returned every time.
        Its properties depend on the first entry in the variants array as well as the keyword arguments specifying the tuning parameters.

        :return: Flavour.
        """
        if not self.is_setup:
            raise SelectorNotFullySetupException("The selector has not been fully setup.")

        if not self.flavour:
            kwargs = self.variants_kwargs
            kwargs['loop_unroll'] = self.loop_unroll_factors[0]

            variant = self.variants[0](self.settings,
                                       self.opencl,
                                       self.device,
                                       **kwargs)

            self.flavour = Selector.Flavour(variant)

        return self.flavour


class EpsilonSelector(Selector):
    """
    The selection process is subdivided into exploration and exploitation phases.
    The performance of a single flavour is investigated during an exploration phase.

    :ivar explore: Distance, given as a number of sub matrices, between two exploration phases.
    :ivar kwargs: Keyword arguments.
    :ivar flavours: Flavours already explored.
    """

    def __init__(self,
                 loop_unroll_factors=(1, 2, 4, 8, 16, 32),
                 explore=5):
        Selector.__init__(self,
                          loop_unroll_factors)

        self.explore = explore

        self.flavours = {}

    def reset(self):
        """
        Reset the set of flavours used up to this point.
        """

        self.flavours = {}

    def get_random_flavor(self):
        """
        Generate a random flavour that has not yet been used.
        """

        if not self.is_setup:
            raise SelectorNotFullySetupException("No variant available.")

        flavour = None
        is_next_flavor = False

        while not is_next_flavor:
            variant = self.variants[np.random.randint(0, len(self.variants))]

            kwargs = self.variants_kwargs
            kwargs['loop_unroll'] = self.loop_unroll_factors[np.random.randint(0,
                                                                               len(self.loop_unroll_factors))]

            flavour = Selector.Flavour(variant(self.settings,
                                               self.opencl,
                                               self.device,
                                               **kwargs))

            if flavour.identifier not in list(self.flavours.keys()):
                self.flavours[flavour.identifier] = flavour
                is_next_flavor = True
            elif len(self.flavours) == len(self.variants) * len(self.loop_unroll_factors):
                is_next_flavor = True

        return flavour

    def get_best_flavor(self):
        """
        Get best performing flavour, based on the performance data gathered up to this point.
        """

        if not self.flavours:
            raise NoFlavorException("No flavor available.")
        else:
            min_flavor_id = None
            min_average_total_runtime = 0

            if sys.version_info.major == 2:
                itr = self.flavours.iteritems()
            if sys.version_info.major == 3:
                itr = self.flavours.items()

            for flavor_id, flavor in itr:
                if min_flavor_id is None:
                    min_flavor_id = flavor_id
                    min_average_total_runtime = flavor.average_total_runtime
                else:
                    if flavor.average_total_runtime < min_average_total_runtime:
                        min_flavor_id = flavor_id
                        min_average_total_runtime = flavor.average_total_runtime

            return self.flavours[min_flavor_id]

    def get_flavour(self):
        """
        Get the flavour for processing the next sub matrix.
        """

        pass


class EpsilonGreedySelector(EpsilonSelector):
    """
    Epsilon-greedy flavour selection.
    """

    def __init__(self,
                 loop_unroll_factors=(1, 2, 4, 8, 16, 32),
                 explore=5):
        EpsilonSelector.__init__(self,
                                 loop_unroll_factors=loop_unroll_factors,
                                 explore=explore)

    def get_flavour(self):
        """
        A random flavour is selected each 'explore' sub matrices.
        Otherwise, the best-performing flavour is selected.
        NOTE: Performance data is also gathered, when the best-performing flavour is selected.
        """

        if self.sub_matrix_count % self.explore == 0:
            flavor = self.get_random_flavor()
        else:
            flavor = self.get_best_flavor()

        return flavor


class VWGreedySelector(EpsilonSelector):
    """
    Vw-greedy flavour selection.
    """

    def __init__(self,
                 loop_unroll_factors=(1, 2, 4, 8, 16, 32),
                 explore=5,
                 factor=3):
        EpsilonSelector.__init__(self,
                                 loop_unroll_factors=loop_unroll_factors,
                                 explore=explore)

        self.factor = factor

    def get_flavour(self):
        """
        The flavour selection is similar to the EpsilonGreedy strategy.
        Here, the performance data gathered is resetted after having processed 'factor * explore' sub matrices.
        """

        if self.sub_matrix_count % self.explore == 0:
            if self.sub_matrix_count % (self.explore * self.factor) == 0:
                self.reset()

            flavor = self.get_random_flavor()
        else:
            flavor = self.get_best_flavor()

        return flavor


class EpsilonDecreasingSelector(EpsilonSelector):
    """
    Epsilon-decreasing flavour selection.
    """

    def __init__(self,
                 loop_unroll_factors=(1, 2, 4, 8, 16, 32),
                 explore=5,
                 delta=1):
        EpsilonSelector.__init__(self,
                                 loop_unroll_factors=loop_unroll_factors,
                                 explore=explore)

        self.delta = delta

    def get_flavour(self):
        """
        The flavour selection is similar to the EpsilonGreedy strategy.
        Here, the value of 'explore' is increased by the value of 'delta' after each exploration phase.
        """

        if self.sub_matrix_count % self.explore == 0:
            flavor = self.get_random_flavor()

            if self.sub_matrix_count != 0:
                self.explore += self.delta
        else:
            flavor = self.get_best_flavor()

        return flavor


class EpsilonFirstSelector(EpsilonSelector):
    """
    Espilon-first flavour selection.
    """

    def __init__(self,
                 loop_unroll_factors=(1, 2, 4, 8, 16, 32),
                 explore=15):
        EpsilonSelector.__init__(self,
                                 loop_unroll_factors=loop_unroll_factors,
                                 explore=explore)

    def get_flavour(self):
        """
        There is a fixed-size exploration phase of 'explore' sub matrices at the beginning of the program execution.
        After this initial phase, the best-performing flavour is always selected.
        """

        if self.sub_matrix_count < self.explore:
            flavor = self.get_random_flavor()
        else:
            flavor = self.get_best_flavor()

        return flavor
