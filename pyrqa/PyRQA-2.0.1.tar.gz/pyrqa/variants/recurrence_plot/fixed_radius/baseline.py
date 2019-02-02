#!/usr/bin/env python

"""
Create recurrence plot using plain python statements.

Input data representation: Column store
Similarity value representation: Byte
Recurrence matrix division: No
"""

import time

import numpy as np

from pyrqa.base_classes import BaseRunnable
from pyrqa.recurrence_analysis import RecurrencePlot
from pyrqa.result import RPResult
from pyrqa.runtimes import MatrixRuntimes, \
    FlavourRuntimesMonolithic

__author__ = "Tobias Rawald"
__copyright__ = "Copyright 2015, 2018 The PyRQA project"
__credits__ = ["Tobias Rawald",
               "Mike Sips"]
__license__ = "Apache-2.0"
__maintainer__ = "Tobias Rawald"
__email__ = "pyrqa@gmx.net"
__status__ = "Development"


class Baseline(RecurrencePlot, BaseRunnable):
    """
    See module description regarding computational properties.
    """

    def __init__(self,
                 settings,
                 verbose=True):
        """
        :param settings: Settings.
        :param verbose: Shall detailed information be printed out during the processing.
        """

        RecurrencePlot.__init__(self,
                                settings=settings,
                                verbose=verbose)

    def reset(self):
        RecurrencePlot.reset(self)

    def create_matrix(self):
        """
        Create matrix
        """
        for index_x in np.arange(self.settings.time_series.number_of_vectors):
            for index_y in np.arange(self.settings.time_series.number_of_vectors):
                distance = self.settings.similarity_measure.get_distance_time_series(self.settings.time_series.data,
                                                                                     self.settings.time_series.data,
                                                                                     self.settings.time_series.embedding_dimension,
                                                                                     self.settings.time_series.time_delay,
                                                                                     index_x,
                                                                                     index_y)

                if self.settings.neighbourhood.contains(distance):
                    self.recurrence_matrix[index_y][index_x] = 1

    def run(self):
        self.reset()

        start = time.time()
        self.create_matrix()
        end = time.time()

        variant_runtimes = FlavourRuntimesMonolithic(execute_computations=end - start)

        number_of_partitions = 1
        matrix_runtimes = MatrixRuntimes(number_of_partitions)
        matrix_runtimes.update_index(0, 0, variant_runtimes)

        result = RPResult(self.settings,
                          matrix_runtimes,
                          recurrence_matrix=self.recurrence_matrix)



        return result
