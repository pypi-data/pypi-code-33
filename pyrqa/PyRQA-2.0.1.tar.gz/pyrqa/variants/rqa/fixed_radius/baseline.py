#!/usr/bin/env python

"""
Baseline RQA implementation
"""

import math
import time

import numpy as np

from pyrqa.base_classes import BaseRunnable
from pyrqa.recurrence_analysis import RQA, Carryover
from pyrqa.result import RQAResult
from pyrqa.runtimes import MatrixRuntimes,\
    FlavourRuntimesMonolithic

__author__ = "Tobias Rawald"
__copyright__ = "Copyright 2015, 2018 The PyRQA project"
__credits__ = ["Tobias Rawald",
               "Mike Sips"]
__license__ = "Apache-2.0"
__maintainer__ = "Tobias Rawald"
__email__ = "pyrqa@gmx.net"
__status__ = "Development"


class Baseline(RQA, Carryover, BaseRunnable):
    """
    Full Matrix
    No Sub Matrices
    Plain Python
    """
    def __init__(self,
                 settings,
                 verbose=True):
        RQA.__init__(self, settings, verbose)
        Carryover.__init__(self, settings, verbose)

        self.__initialise()

    def __initialise(self):
        # Bypass possible symmetry of similarity matrix
        self.diagonal_length_carryover = np.zeros(self.settings.time_series.number_of_vectors * 2 - 1, dtype=np.uint32)

    def reset(self):
        RQA.reset(self)
        Carryover.reset(self)
        self.__initialise()

    def run(self):
        start = time.time()

        self.reset()

        for index_x in np.arange(self.settings.time_series.number_of_vectors):
            vertical_index = index_x

            for index_y in np.arange(self.settings.time_series.number_of_vectors):
                diagonal_index = self.settings.time_series.number_of_vectors - 1 + (index_y - index_x)

                distance = self.settings.similarity_measure.get_distance_time_series(self.settings.time_series.data,
                                                                                     self.settings.time_series.data,
                                                                                     self.settings.time_series.embedding_dimension,
                                                                                     self.settings.time_series.time_delay,
                                                                                     index_x,
                                                                                     index_y)

                if self.settings.neighbourhood.contains(distance):
                    # Recurrence points
                    self.recurrence_points[vertical_index] += 1

                    # Diagonal lines
                    if math.fabs(index_y - index_x) >= self.settings.theiler_corrector:
                        self.diagonal_length_carryover[diagonal_index] += 1

                    # Vertical lines
                    self.vertical_length_carryover[vertical_index] += 1

                    # White vertical lines
                    if self.white_vertical_length_carryover[vertical_index] > 0:
                        self.white_vertical_frequency_distribution[self.white_vertical_length_carryover[vertical_index] - 1] += 1

                    self.white_vertical_length_carryover[vertical_index] = 0
                else:
                    # Diagonal lines
                    if self.diagonal_length_carryover[diagonal_index] > 0:
                        self.diagonal_frequency_distribution[self.diagonal_length_carryover[diagonal_index] - 1] += 1

                    self.diagonal_length_carryover[diagonal_index] = 0

                    # Vertical lines
                    if self.vertical_length_carryover[vertical_index] > 0:
                        self.vertical_frequency_distribution[self.vertical_length_carryover[vertical_index] - 1] += 1

                    self.vertical_length_carryover[vertical_index] = 0

                    # White vertical lines
                    self.white_vertical_length_carryover[vertical_index] += 1

        for line_length in self.diagonal_length_carryover:
            if line_length > 0:
                self.diagonal_frequency_distribution[line_length - 1] += 1

        for line_length in self.vertical_length_carryover:
            if line_length > 0:
                self.vertical_frequency_distribution[line_length - 1] += 1

        for line_length in self.white_vertical_length_carryover:
            if line_length > 0:
                self.white_vertical_frequency_distribution[line_length - 1] += 1

        end = time.time()

        variant_runtimes = FlavourRuntimesMonolithic(execute_computations=end - start)

        number_of_partitions = 1
        matrix_runtimes = MatrixRuntimes(number_of_partitions)
        matrix_runtimes.update_index(0,
                                     0,
                                     variant_runtimes)

        result = RQAResult(self.settings,
                           matrix_runtimes,
                           recurrence_points=self.recurrence_points,
                           diagonal_frequency_distribution=self.diagonal_frequency_distribution,
                           vertical_frequency_distribution=self.vertical_frequency_distribution,
                           white_vertical_frequency_distribution=self.white_vertical_frequency_distribution)

        return result
