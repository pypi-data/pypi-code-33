#!/usr/bin/env python

"""
Recurrence analysis
"""

import math
import sys

import numpy as np

from pyrqa.base_classes import BaseSettings, \
    BaseVerbose
from pyrqa.processing_order import Bulk, \
    Diagonal, \
    Vertical

__author__ = "Tobias Rawald"
__copyright__ = "Copyright 2015, 2018 The PyRQA project"
__credits__ = ["Tobias Rawald",
               "Mike Sips"]
__license__ = "Apache-2.0"
__maintainer__ = "Tobias Rawald"
__email__ = "pyrqa@gmx.net"
__status__ = "Development"


if sys.version_info.major == 2:
    import Queue as queue
if sys.version_info.major == 3:
    import queue


class RecurrencePlot(BaseSettings,
                     BaseVerbose):
    """
    Recurrence Plot.

    :ivar recurrence_matrix: Recurrence matrix.
    """

    def __init__(self,
                 settings,
                 verbose):
        BaseSettings.__init__(self,
                              settings)
        BaseVerbose.__init__(self,
                             verbose)

        self.__initialise()

    def __initialise(self):
        """
        Initialise the instance variables.
        """

        self.recurrence_matrix = np.zeros((self.settings.time_series.number_of_vectors,
                                           self.settings.time_series.number_of_vectors),
                                          dtype=np.uint8)

    def reset(self):
        """
        Reset the instance variables.
        """

        self.__initialise()


class RQA(BaseSettings, BaseVerbose):
    """
    Recurrence quantification analysis.

    :ivar recurrence_points: Local recurrence points.
    :ivar diagonal_frequency_distribution: Frequency distribution of diagonal lines.
    :ivar vertical_frequency_distribution: Frequency distribution of vertical lines.
    :ivar white_vertical_frequency_distribution: Frequency distribution of white vertical lines.
    """

    def __init__(self,
                 settings,
                 verbose):
        BaseSettings.__init__(self,
                              settings)
        BaseVerbose.__init__(self,
                             verbose)

        self.__initialise()

    def __initialise(self):
        """
        Initialise the instance variables.
        """

        self.recurrence_points = self.get_empty_recurrence_points()
        self.diagonal_frequency_distribution = self.get_empty_global_frequency_distribution()
        self.vertical_frequency_distribution = self.get_empty_global_frequency_distribution()
        self.white_vertical_frequency_distribution = self.get_empty_global_frequency_distribution()

    def reset(self):
        """
        Reset the instance variables.
        """

        self.__initialise()

    def get_empty_recurrence_points(self):
        """
        Get empty recurrence points.

        :return: Empty recurrence points.
        :rtype: 1D array.
        """

        return np.zeros(self.settings.time_series.number_of_vectors,
                        dtype=np.uint32)

    def get_empty_global_frequency_distribution(self):
        """
        Get empty frequency distribution.

        :returns: Empty global frequency distribution.
        :rtype: 1D array.
        """

        return np.zeros(self.settings.time_series.number_of_vectors,
                        dtype=np.uint64)

    def extent_diagonal_frequency_distribution(self):
        """
        Extent the content of the diagonal frequency distribution.
        """

        if self.settings.is_matrix_symmetric:
            self.diagonal_frequency_distribution += self.diagonal_frequency_distribution
            if not self.settings.theiler_corrector:
                self.diagonal_frequency_distribution[-1] -= 1


class SubMatrix(object):
    """
    Sub matrix.

    :ivar partition_index_x: X index of sub matrix in partitioned global recurrence matrix.
    :ivar partition_index_y: Y index of sub matrix in partitioned global recurrence matrix.
    :ivar start_x: Global index for first vector (X dimension).
    :ivar start_y: Global index for first vector (Y dimension).
    :ivar dim_x: Number of vectors (X dimension).
    :ivar dim_y: Number of vectors (Y dimension).
    """

    def __init__(self, partition_index_x, partition_index_y, dim_x, start_x, dim_y, start_y):
        self.partition_index_x = partition_index_x
        self.partition_index_y = partition_index_y
        self.start_x = start_x
        self.start_y = start_y
        self.dim_x = dim_x
        self.dim_y = dim_y

        self.data = None

    @property
    def diagonal_offset(self):
        """
        Offset for detecting diagonal lines.
        """

        if self.partition_index_x < self.partition_index_y:
            return 1

        return 0

    @property
    def elements(self):
        """
        Number of matrix elements.
        """
        return self.dim_x * self.dim_y

    @staticmethod
    def bits_per_element(data_type):
        """
        Bits per element.

        :param data_type: Data type.
        :return: Bits per element.
        """
        return np.dtype(data_type).itemsize * 8

    def elements_byte(self):
        """ Number of elements based on byte representation. """
        return self.dim_x * self.dim_y

    def elements_bit(self, data_type):
        """
        Number of elements based on bit representation.

        :param data_type: Data type.
        :return: Number of elements.
        """
        return self.dim_x * math.ceil(float(self.dim_y) / self.bits_per_element(data_type))

    def size_byte(self, data_type):
        """
        Size based on byte representation.

        :param data_type: Data type.
        :return: Size.
        """
        return self.elements_byte() * np.dtype(data_type).itemsize

    def size_bit(self, data_type):
        """
        Size based on bit representation.

        :param data_type: Data type.
        :return: Size.
        """
        return self.elements_bit(data_type) * np.dtype(data_type).itemsize

    def set_empty_data_byte(self, data_type):
        """
        Set empty data based on byte representation.

        :param data_type: Data type.
        :return: Empty data.
        """
        self.data = np.zeros(self.elements_byte(), dtype=data_type)

    def set_empty_data_bit(self, data_type):
        """
        Set empty data based on bit representation.

        :param data_type: Data type.
        :return: Empty data.
        """
        self.data = np.zeros(self.elements_bit(data_type), dtype=data_type)

    def __str__(self):
        return "Sub Matrix\n" \
               "----------\n" \
               "\n" \
               "Partition Index X: %d\n" \
               "Partition Index Y: %d\n" \
               "Start X: %d\n" \
               "Start Y: %d\n"\
               "Dim X: %d\n" \
               "Dim Y: %d\n" % (self.partition_index_x,
                                self.partition_index_y,
                                self.start_y,
                                self.start_x,
                                self.dim_x,
                                self.dim_y)


class SubMatrices(BaseSettings):
    """
    Processing of sub matrices.

    :ivar edge_length: Inital edge length of sub matrix.
    :ivar processing_order: Processing order of the sub matrices.
    """

    def __init__(self,
                 settings,
                 edge_length,
                 processing_order):
        BaseSettings.__init__(self, settings)

        self.edge_length = edge_length
        self.number_of_partitions = None
        self.processing_order = processing_order

        self.number_of_paritions = 0
        self.sub_matrix_queues = None

        self.__initialise()

    def __initialise(self):
        """ Initialise the instance variables. """
        self.create_sub_matrices()

    def reset(self):
        """ Reset the instance variables. """
        self.__initialise()

    def create_sub_matrices(self):
        """
        Create sub matrices according to the given processing order.
        Each task queue represents an execution level.
        """
        max_edge_length = math.pow(2, 16) - 1
        self.edge_length = max_edge_length if self.edge_length > max_edge_length else self.edge_length
        self.number_of_partitions = int(math.ceil(float(self.settings.time_series.number_of_vectors) / self.edge_length))

        self.sub_matrix_queues = []
        for partition_index_x in np.arange(self.number_of_partitions):
            for partition_index_y in np.arange(self.number_of_partitions):
                if partition_index_x == self.number_of_partitions - 1:
                    dim_x = self.settings.time_series.number_of_vectors - partition_index_x * self.edge_length
                    start_x = partition_index_x * self.edge_length
                else:
                    dim_x = self.edge_length
                    start_x = partition_index_x * dim_x

                if partition_index_y == self.number_of_partitions - 1:
                    dim_y = self.settings.time_series.number_of_vectors - partition_index_y * self.edge_length
                    start_y = partition_index_y * self.edge_length
                else:
                    dim_y = self.edge_length
                    start_y = partition_index_y * dim_y

                sub_matrix = SubMatrix(partition_index_x,
                                       partition_index_y,
                                       dim_x,
                                       start_x,
                                       dim_y,
                                       start_y)

                queue_index = None
                if self.processing_order == Diagonal:
                    queue_index = partition_index_x + partition_index_y

                elif self.processing_order == Vertical:
                    queue_index = partition_index_y

                elif self.processing_order == Bulk:
                    queue_index = 0

                if len(self.sub_matrix_queues) <= queue_index:
                    self.sub_matrix_queues.append(queue.Queue())

                self.sub_matrix_queues[queue_index].put(sub_matrix)


class Carryover(BaseSettings, BaseVerbose):
    """
    Perform recurrence quantification analysis based on multiple sub matrices

    :ivar diagonal_length_carryover: Diagonal line length carryover.
    :ivar diagonal_index_carryover: Diagonal index carryover.
    :ivar vertical_length_carryover: Vertical line length carryover.
    :ivar vertical_index_carryover: Vertical index carryover.
    :ivar white_vertical_length_carryover: White vertical line length carryover.
    :ivar white_vertical_flag_carryover: White vertical flag carryover.
    """
    def __init__(self, settings, verbose):
        BaseSettings.__init__(self, settings)
        BaseVerbose.__init__(self, verbose)

        self.__initialise()

    def __initialise(self):
        """ Initialise the instance variables. """
        if self.settings.is_matrix_symmetric:
            self.diagonal_length_carryover = np.zeros(self.settings.time_series.number_of_vectors, dtype=np.uint32)
            self.diagonal_index_carryover = np.zeros(self.settings.time_series.number_of_vectors, dtype=np.uint32)
        else:
            self.diagonal_length_carryover = np.zeros(self.settings.time_series.number_of_vectors * 2 - 1, dtype=np.uint32)
            self.diagonal_index_carryover = np.zeros(self.settings.time_series.number_of_vectors * 2 - 1, dtype=np.uint32)

        self.vertical_length_carryover = np.zeros(self.settings.time_series.number_of_vectors, dtype=np.uint32)
        self.vertical_index_carryover = np.zeros(self.settings.time_series.number_of_vectors, dtype=np.uint32)

        self.white_vertical_length_carryover = np.zeros(self.settings.time_series.number_of_vectors, dtype=np.uint32)
        self.white_vertical_flag_carryover = np.zeros(self.settings.time_series.number_of_vectors, dtype=np.uint8)

    def reset(self):
        """ Reset the instance variables. """
        self.__initialise()


class RecurrencePlotSubMatrices(RecurrencePlot, SubMatrices):
    """
    Combination of:
    - RecurrencePlot and
    - SubMatrices.
    """
    def __init__(self,
                 settings,
                 verbose,
                 edge_length,
                 processing_order):

        RecurrencePlot.__init__(self, settings, verbose)
        SubMatrices.__init__(self, settings, edge_length, processing_order)

    def reset(self):
        """ Reset the instance variables. """
        RecurrencePlot.reset(self)
        SubMatrices.reset(self)

    def set_sub_matrix_data(self,
                            sub_matrix):
        """
        Set sub matrix data in global recurrence matrix.

        :param sub_matrix: Sub matrix.
        """
        sub_matrix.data = sub_matrix.data.reshape(sub_matrix.dim_y, sub_matrix.dim_x)
        self.recurrence_matrix[sub_matrix.start_y:sub_matrix.start_y + sub_matrix.dim_y, sub_matrix.start_x:sub_matrix.start_x + sub_matrix.dim_x] = sub_matrix.data

    def process_sub_matrix(self):
        """
        Process a single sub matrix.
        """
        pass


class RQASubMatricesCarryover(RQA, SubMatrices, Carryover):
    """
    Combination of:
    - RQA,
    - SubMatrices,
    - OpenCL and
    - Carryover.
    """
    def __init__(self,
                 settings,
                 verbose,
                 edge_length,
                 processing_order):

        RQA.__init__(self, settings, verbose)
        SubMatrices.__init__(self, settings, edge_length, processing_order)
        Carryover.__init__(self, settings, verbose)

    def reset(self):
        """
        Reset the instance variables.
        """
        RQA.reset(self)
        SubMatrices.reset(self)
        Carryover.reset(self)

    def get_empty_local_frequency_distribution(self):
        """
        Get empty local frequency distribution.

        :returns: Empty local frequency distribution.
        """
        return np.zeros(self.settings.time_series.number_of_vectors, dtype=np.uint32)

    @staticmethod
    def recurrence_points_start(sub_matrix):
        """
        Start index of the sub matrix specific segment within the global recurrence point array.

        :param sub_matrix: Sub matrix.
        :return: Recurrence points start.
        """
        return sub_matrix.start_x

    @staticmethod
    def recurrence_points_end(sub_matrix):
        """
        End index of the sub matrix specific segment within the global recurrence point array.

        :param sub_matrix: Sub matrix.
        :return: Recurrence points end.
        """
        return sub_matrix.start_x + sub_matrix.dim_x

    def get_recurrence_points(self, sub_matrix):
        """
        Get the sub matrix specific segment within the global recurrence points array.

        :param sub_matrix: Sub matrix.
        :returns: Sub array of the global recurrence points array.
        """
        start = self.recurrence_points_start(sub_matrix)
        end = self.recurrence_points_end(sub_matrix)

        return self.recurrence_points[start:end]

    def set_recurrence_points(self, sub_matrix):
        """
        Set the sub matrix specific segment within the global recurrence points array.

        :param sub_matrix: Sub matrix.
        :param recurrence_points: Recurrence points segment.
        """
        start = self.recurrence_points_start(sub_matrix)
        end = self.recurrence_points_end(sub_matrix)

        self.recurrence_points[start:end] = sub_matrix.recurrence_points

    @staticmethod
    def vertical_length_carryover_start(sub_matrix):
        """
        Start index of the sub matrix specific segment within the global vertical length carryover array.

        :param sub_matrix: Sub matrix.
        :return: Vertical length carryover start.
        """
        return sub_matrix.start_x

    @staticmethod
    def vertical_length_carryover_end(sub_matrix):
        """
        End index of the sub matrix specific segment within the global vertical length carryover array.

        :param sub_matrix: Sub matrix.
        :return: Vertical length carryover end.
        """
        return sub_matrix.start_x + sub_matrix.dim_x

    def get_vertical_length_carryover(self, sub_matrix):
        """
        Get the sub matrix specific segment within the global vertical length carryover array.

        :param sub_matrix: Sub matrix.
        :returns: Sub array of the global vertical length carryover array.
        """
        start = self.vertical_length_carryover_start(sub_matrix)
        end = self.vertical_length_carryover_end(sub_matrix)

        return self.vertical_length_carryover[start:end]

    def set_vertical_length_carryover(self, sub_matrix):
        """
        Set the sub matrix specific segment within the global vertical length carryover array.

        :param sub_matrix: Sub matrix
        :param vertical_length_carryover: Verical length carryover segment.
        """
        start = self.vertical_length_carryover_start(sub_matrix)
        end = self.vertical_length_carryover_end(sub_matrix)

        self.vertical_length_carryover[start:end] = sub_matrix.vertical_length_carryover

    @staticmethod
    def vertical_index_carryover_start(sub_matrix):
        """
        Start index of the sub matrix specific segment within the global vertical index carryover array.

        :param sub_matrix: Sub matrix.
        :return: Vertical index carryover start.
        """
        return sub_matrix.start_x

    @staticmethod
    def vertical_index_carryover_end(sub_matrix):
        """
        End index of the sub matrix specific segment within the global vertical index carryover array.

        :param sub_matrix: Sub matrix.
        :return: Vertical index carryover end.
        """
        return sub_matrix.start_x + sub_matrix.dim_x

    def get_vertical_index_carryover(self, sub_matrix):
        """
        Get the sub matrix specific segment within the global vertical index carryover array.

        :param sub_matrix: Sub matrix.
        :returns: Sub array of the global vertical index carryover array.
        """
        start = self.vertical_index_carryover_start(sub_matrix)
        end = self.vertical_index_carryover_end(sub_matrix)

        return self.vertical_index_carryover[start:end]

    def set_vertical_index_carryover(self, sub_matrix):
        """
        Set the sub matrix specific segment within the global vertical index carryover array.

        :param sub_matrix: Sub matrix.
        :param vertical_index_carryover: Vertical index carryover segment.
        """
        start = self.vertical_index_carryover_start(sub_matrix)
        end = self.vertical_index_carryover_end(sub_matrix)

        self.vertical_index_carryover[start:end] = sub_matrix.vertical_index_carryover

    @staticmethod
    def white_vertical_length_carryover_start(sub_matrix):
        """
        Start index of the sub matrix specific segment of the global white vertical length carryover array.

        :param sub_matrix: Sub matrix.
        :return: White vertical length carryover start.
        """
        return sub_matrix.start_x

    @staticmethod
    def white_vertical_length_carryover_end(sub_matrix):
        """
        End index of the sub matrix specific segment of the global white vertical length carryover array.

        :param sub_matrix: Sub matrix.
        :return: White vertical length carryover end.
        """

        return sub_matrix.start_x + sub_matrix.dim_x

    def get_white_vertical_length_carryover(self, sub_matrix):
        """
        Get the sub matrix specific segment of the global white vertical length carryover array.

        :param sub_matrix: Sub matrix.
        :returns: Sub array of the global white vertical length carryover array.
        """
        start = self.white_vertical_length_carryover_start(sub_matrix)
        end = self.white_vertical_length_carryover_end(sub_matrix)

        return self.white_vertical_length_carryover[start:end]

    def set_white_vertical_length_carryover(self, sub_matrix):
        """
        Set the sub matrix specific segment of the global white vertical length carryover array.

        :param sub_matrix: Sub matrix.
        :param white_vertical_length_carryover: White vertical length carryover segment.
        """
        start = self.white_vertical_length_carryover_start(sub_matrix)
        end = self.white_vertical_length_carryover_end(sub_matrix)

        self.white_vertical_length_carryover[start:end] = sub_matrix.white_vertical_length_carryover

    @staticmethod
    def white_vertical_flag_carryover_start(sub_matrix):
        """
        Start index of the sub matrix specific segment of the global white vertical flag carryover array.

        :param sub_matrix: Sub matrix.
        :return: White vertical flag carryover start.
        """
        return sub_matrix.start_x

    @staticmethod
    def white_vertical_flag_carryover_end(sub_matrix):
        """
        End index of the sub matrix specific segment of the global white vertical flag carryover array.

        :param sub_matrix: Sub matrix.
        :return: White vertical flag carryover end.
        """
        return sub_matrix.start_x + sub_matrix.dim_x

    def get_white_vertical_flag_carryover(self, sub_matrix):
        """
        Get the sub matrix specific segment of the global white vertical flag carryover array.

        :param sub_matrix: Sub matrix.
        :return: Sub array of the global white vertical flag carryover array.
        """
        start = self.white_vertical_flag_carryover_start(sub_matrix)
        end = self.white_vertical_flag_carryover_end(sub_matrix)

        return self.white_vertical_flag_carryover[start:end]

    def set_white_vertical_flag_carryover(self, sub_matrix):
        """
        Set the sub matrix specific segment of the global white vertical flag carryover array.

        :param sub_matrix: Sub matrix.
        :param white_vertical_flag_carryover: White vertical flag carryover segment.
        """
        start = self.white_vertical_flag_carryover_start(sub_matrix)
        end = self.white_vertical_flag_carryover_end(sub_matrix)

        self.white_vertical_flag_carryover[start:end] = sub_matrix.white_vertical_flag_carryover

    def diagonal_length_carryover_start(self, sub_matrix):
        """
        Start index of the sub matrix specific segment of the global diagonal length carryover array.

        :param sub_matrix: Sub matrix.
        :return: Diagonal length carryover start.
        """
        if self.settings.is_matrix_symmetric:
            if sub_matrix.partition_index_x < sub_matrix.partition_index_y:
                return sub_matrix.start_y - (sub_matrix.start_x + sub_matrix.dim_x)

            return sub_matrix.start_x - sub_matrix.start_y

        return (self.settings.time_series.number_of_vectors - 1) + (sub_matrix.start_x - sub_matrix.dim_y + 1) - sub_matrix.start_y

    def diagonal_length_carryover_end(self, sub_matrix):
        """
        End index of the sub matrix specific segment of the global diagonal length carryover array.

        :param sub_matrix: Sub matrix
        :return: Diagonal length carryover end.
        """

        if self.settings.is_matrix_symmetric:
            return self.diagonal_length_carryover_start(sub_matrix) + sub_matrix.dim_x

        return self.diagonal_length_carryover_start(sub_matrix) + (sub_matrix.dim_x + sub_matrix.dim_y - 1)

    def get_diagonal_length_carryover(self, sub_matrix):
        """
        Get the sub matrix specific segment of the global diagonal length carryover array.

        :param sub_matrix: Sub matrix.
        :returns: Sub array of global diagonal length carryover array.
        """
        start = self.diagonal_length_carryover_start(sub_matrix)
        end = self.diagonal_length_carryover_end(sub_matrix)

        return self.diagonal_length_carryover[start:end]

    def set_diagonal_length_carryover(self, sub_matrix):
        """
        Set the sub matrix specific segment of the global diagonal length carryover array.

        :param sub_matrix: Sub matrix.
        :param diagonal_length_carryover: Diagonal length carryover segment.
        """
        start = self.diagonal_length_carryover_start(sub_matrix)
        end = self.diagonal_length_carryover_end(sub_matrix)

        self.diagonal_length_carryover[start:end] = sub_matrix.diagonal_length_carryover

    def diagonal_index_carryover_start(self, sub_matrix):
        """
        Start index of the sub matrix specific segment of the global diagonal index carryover array.

        :param sub_matrix: Sub matrix.
        :return: Diagonal index carryover start.
        """
        if self.settings.is_matrix_symmetric:
            if sub_matrix.partition_index_x < sub_matrix.partition_index_y:
                return sub_matrix.start_y - (sub_matrix.start_x + sub_matrix.dim_x)

            return sub_matrix.start_x - sub_matrix.start_y

        return (self.settings.time_series.number_of_vectors - 1) + (sub_matrix.start_x - sub_matrix.dim_y + 1) - sub_matrix.start_y

    def diagonal_index_carryover_end(self, sub_matrix):
        """
        End index of the sub matrix specific segment of the global diagonal index carryover array.

        :param sub_matrix: Sub matrix.
        :return: Diagonal index carryover end.
        """
        if self.settings.is_matrix_symmetric:
            return self.diagonal_index_carryover_start(sub_matrix) + sub_matrix.dim_x

        return self.diagonal_index_carryover_start(sub_matrix) + (sub_matrix.dim_x + sub_matrix.dim_y - 1)

    def get_diagonal_index_carryover(self, sub_matrix):
        """
        Get the sub matrix specific segment of the global diagonal index carryover array.

        :param sub_matrix: Sub matrix.
        :returns: Sub array of global diagonal index carryover array.
        """
        start = self.diagonal_index_carryover_start(sub_matrix)
        end = self.diagonal_index_carryover_end(sub_matrix)

        return self.diagonal_index_carryover[start:end]

    def set_diagonal_index_carryover(self, sub_matrix):
        """
        Set the sub matrix specific segment of the global diagonal index carryover array.

        :param sub_matrix: Sub matrix.
        :param diagonal_index_carryover: Diagonal index carryover segment.
        """
        start = self.diagonal_index_carryover_start(sub_matrix)
        end = self.diagonal_index_carryover_end(sub_matrix)

        self.diagonal_index_carryover[start:end] = sub_matrix.diagonal_index_carryover

    def post_process_length_carryovers(self):
        """ Post process length carryover buffers. """
        for line_length in self.diagonal_length_carryover[self.diagonal_length_carryover > 0]:
            self.diagonal_frequency_distribution[line_length - 1] += 1

        for line_length in self.vertical_length_carryover[self.vertical_length_carryover > 0]:
            self.vertical_frequency_distribution[line_length - 1] += 1

        for line_length in self.white_vertical_length_carryover[self.white_vertical_length_carryover > 0]:
            self.white_vertical_frequency_distribution[line_length - 1] += 1

    def post_process_vertical_index_carryover(self):
        """ Post process white vertical index carryover buffer. """
        count_outer = 0
        count_inner = 0

        for vertical_idx in self.vertical_index_carryover:
            line_length = self.settings.time_series.number_of_vectors - vertical_idx - 1
            count_outer += 1

            if line_length > 0:
                count_inner += 1
                self.white_vertical_frequency_distribution[line_length - 1] += 1

    @staticmethod
    def get_diagonal_offset(sub_matrix):
        """
        Get diagonal offset.

        :param sub_matrix: Sub matrix.
        :return: Diagonal offset.
        """
        if sub_matrix.partition_index_x < sub_matrix.partition_index_y:
            return 1

        return 0

    def process_sub_matrix_queue(self):
        """
        Processing of a single sub matrix queue.
        """
        pass
