#!/usr/bin/env python

"""
Recurrence analysis runtimes.
"""

import numpy as np

from pyrqa.exceptions import NoSubMatrixRuntimesAvailableException

__author__ = "Tobias Rawald"
__copyright__ = "Copyright 2015, 2018 The PyRQA project"
__credits__ = ["Tobias Rawald",
               "Mike Sips"]
__license__ = "Apache-2.0"
__maintainer__ = "Tobias Rawald"
__email__ = "pyrqa@gmx.net"
__status__ = "Development"


class OperatorRuntimes(object):
    """
    Operator runtimes.

    :ivar transfer_to_device: Data transfer from the host to the computing device.
    :ivar execute_computations: Computation execution.
    :ivar transfer_from_device: Data transfer from the computing device to the host.
    """
    def __init__(self,
                 transfer_to_device=.0,
                 execute_computations=.0,
                 transfer_from_device=.0):
        self.transfer_to_device = transfer_to_device
        self.execute_computations = execute_computations
        self.transfer_from_device = transfer_from_device

    @property
    def total(self):
        """
        Total of transfer_to_device, execute_computations and transfer_from_device.
        """

        return self.transfer_to_device + \
               self.execute_computations + \
               self.transfer_from_device

    def __add__(self, other):
        return OperatorRuntimes(transfer_to_device=self.transfer_to_device + other.transfer_to_device,
                                execute_computations=self.execute_computations + other.execute_computations,
                                transfer_from_device=self.transfer_from_device + other.transfer_from_device)

    def __radd__(self, other):
        return OperatorRuntimes(transfer_to_device=self.transfer_to_device + other.transfer_to_device,
                                execute_computations=self.execute_computations + other.execute_computations,
                                transfer_from_device=self.transfer_from_device + other.transfer_from_device)

    def __str__(self):
        return "Runtimes\n" \
               "--------\n" \
               "Transfer to Device: %.4fs\n" \
               "Execute computations: %4fs\n" \
               "Transfer from Device: %.4fs\n" \
               "Total: %.4fs\n" % (self.transfer_to_device,
                                   self.execute_computations,
                                   self.transfer_from_device,
                                   self.total)


class FlavourRuntimesMonolithic(OperatorRuntimes):
    """
    Runtimes of a flavour without the separation into multiple analytical operators.
    """

    def __init__(self,
                 transfer_to_device=.0,
                 execute_computations=.0,
                 transfer_from_device=.0):
        OperatorRuntimes.__init__(self,
                                  transfer_to_device=transfer_to_device,
                                  execute_computations=execute_computations,
                                  transfer_from_device=transfer_from_device)


class FlavourRuntimesMultipleOperators(object):
    """
    Runtimes of a flavour subdivided into multiple analytical operators.

    :ivar create_matrix_runtimes: Runtimes for creating the recurrence matrix.
    :ivar detect_vertical_lines_runtimes: Runtimes for detecting vertical lines.
    :ivar detect_diagonal_lines_runtimes: Runtimes for detecting diagonal lines.
    """

    def __init__(self):
        self.create_matrix_runtimes = None
        self.detect_vertical_lines_runtimes = None
        self.detect_diagonal_lines_runtimes = None

    @property
    def total(self):
        """
        Cumulative total runtime of all analytical operators.
        """

        total = .0

        if self.create_matrix_runtimes:
            total += self.create_matrix_runtimes.total
        if self.detect_vertical_lines_runtimes:
            total += self.detect_vertical_lines_runtimes.total
        if self.detect_diagonal_lines_runtimes:
            total += self.detect_diagonal_lines_runtimes.total

        return total

    @property
    def transfer_to_device(self):
        """
        Cumulative runtime of all analytical operators regarding the transfer of data to the OpenCL compute devices.
        """

        transfer_to_device = .0

        if self.create_matrix_runtimes:
            transfer_to_device += self.create_matrix_runtimes.transfer_to_device
        if self.detect_vertical_lines_runtimes:
            transfer_to_device += self.detect_vertical_lines_runtimes.transfer_to_device
        if self.detect_diagonal_lines_runtimes:
            transfer_to_device += self.detect_diagonal_lines_runtimes.transfer_to_device

        return transfer_to_device

    @property
    def execute_computations(self):
        """
        Cumulative runtime of all analytical operators regarding the execution of the computations on the OpenCL compute devices.
        """

        execute_computations = .0

        if self.create_matrix_runtimes:
            execute_computations += self.create_matrix_runtimes.execute_computations
        if self.detect_vertical_lines_runtimes:
            execute_computations += self.detect_vertical_lines_runtimes.execute_computations
        if self.detect_diagonal_lines_runtimes:
            execute_computations += self.detect_diagonal_lines_runtimes.execute_computations

        return execute_computations

    @property
    def transfer_from_device(self):
        """
        Cumulative runtime of all analytical operators regarding the transfer of data from the OpenCL compute devices.
        """

        transfer_from_device = .0

        if self.create_matrix_runtimes:
            transfer_from_device += self.create_matrix_runtimes.transfer_from_device
        if self.detect_vertical_lines_runtimes:
            transfer_from_device += self.detect_vertical_lines_runtimes.transfer_from_device
        if self.detect_diagonal_lines_runtimes:
            transfer_from_device += self.detect_diagonal_lines_runtimes.transfer_from_device

        return transfer_from_device


class MatrixRuntimes(object):
    """
    Flavour runtimes captured individually for each sub matrix of the global recurrence matrix.
    """

    def __init__(self,
                 number_of_partitions):
        self.number_of_partitions = number_of_partitions
        self.sub_matrix_runtimes = [[None for _ in np.arange(number_of_partitions)] for _ in np.arange(number_of_partitions)]

    @property
    def transfer_to_device(self):
        """
        Cumulative runtime of all sub matrices regarding the transfer of data to the OpenCL compute devices.
        """

        transfer_to_device = .0

        for index_y in np.arange(self.number_of_partitions):
            for index_x in np.arange(self.number_of_partitions):
                if self.sub_matrix_runtimes[index_y][index_x] is not None:
                    transfer_to_device += self.sub_matrix_runtimes[index_y][index_x].transfer_to_device
                else:
                    NoSubMatrixRuntimesAvailableException("No sub matrix runtimes avaiblable for index_y: %d, index_x: %d." % (index_y, index_x))

        return transfer_to_device

    @property
    def execute_computations(self):
        """
        Cumulative runtime of all sub matrices regarding the execution of the computation on the OpenCL compute devices.
        """

        execute_computations = .0

        for index_y in np.arange(self.number_of_partitions):
            for index_x in np.arange(self.number_of_partitions):
                if self.sub_matrix_runtimes[index_y][index_x] is not None:
                    execute_computations += self.sub_matrix_runtimes[index_y][index_x].execute_computations
                else:
                    NoSubMatrixRuntimesAvailableException("No sub matrix runtimes avaiblable for index_y: %d, index_x: %d." % (index_y, index_x))

        return execute_computations

    @property
    def transfer_from_device(self):
        """
        Cumulative runtime of all sub matrices regarding the transfer of data from the OpenCL compute devices.
        """

        transfer_from_device = .0

        for index_y in np.arange(self.number_of_partitions):
            for index_x in np.arange(self.number_of_partitions):
                if self.sub_matrix_runtimes[index_y][index_x] is not None:
                    transfer_from_device += self.sub_matrix_runtimes[index_y][index_x].transfer_from_device
                else:
                    NoSubMatrixRuntimesAvailableException("No sub matrix runtimes avaiblable for index_y: %d, index_x: %d." % (index_y, index_x))

        return transfer_from_device

    @property
    def total(self):
        """
        Cumulative total runtime of all sub matrices.
        """
        total = .0

        for index_y in np.arange(self.number_of_partitions):
            for index_x in np.arange(self.number_of_partitions):
                if self.sub_matrix_runtimes[index_y][index_x] is not None:
                    total += self.sub_matrix_runtimes[index_y][index_x].total
                else:
                    NoSubMatrixRuntimesAvailableException("No sub matrix runtimes avaiblable for index_y: %d, index_x: %d." % (index_y, index_x))

        return total

    def update_sub_matrix(self,
                          sub_matrix,
                          runtimes):
        """
        Update an individual element of matrix runtimes using a sub matrix.

        :param sub_matrix: Sub matrix processed.
        :param runtimes: Runtimes of sub matrix.
        """

        self.sub_matrix_runtimes[sub_matrix.partition_index_y][sub_matrix.partition_index_x] = runtimes

    def update_index(self,
                     partition_index_x,
                     partition_index_y,
                     runtimes):
        """
        Update an individual element of matrix runtimes using the X and Y index of a sub matrix

        :param partition_index_x: X index of the sub matrix.
        :param partition_index_y: Y index of the sub matrix.
        :param runtimes: Runtimes of the sub matrix.
        :return:
        """

        self.sub_matrix_runtimes[partition_index_y][partition_index_x] = runtimes
