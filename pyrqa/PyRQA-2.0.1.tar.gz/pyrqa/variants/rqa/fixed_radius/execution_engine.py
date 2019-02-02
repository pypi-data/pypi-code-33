#!/usr/bin/env python

"""
Execution engine for conducting recurrence quantification analysis using the fixed radius neighbourhood.
"""

import copy
import sys
import time

from threading import Thread

from pyrqa.variants.rqa.fixed_radius.column_materialisation_uncompressed_byte_no_recycling import ColumnMaterialisationUncompressedByteNoRecycling
from pyrqa.base_classes import BaseRunnable
from pyrqa.exceptions import SubMatrixNotProcessedException
from pyrqa.opencl import OpenCL
from pyrqa.processing_order import Diagonal
from pyrqa.recurrence_analysis import RQASubMatricesCarryover
from pyrqa.result import RQAResult
from pyrqa.runtimes import MatrixRuntimes, \
    FlavourRuntimesMonolithic
from pyrqa.selector import SingleSelector
from pyrqa.types import MatrixRepresentation

if sys.version_info.major == 2:
    import Queue as queue
if sys.version_info.major == 3:
    import queue

__author__ = "Tobias Rawald"
__copyright__ = "Copyright 2015, 2018 The PyRQA project"
__credits__ = ["Tobias Rawald",
               "Mike Sips"]
__license__ = "Apache-2.0"
__maintainer__ = "Tobias Rawald"
__email__ = "pyrqa@gmx.net"
__status__ = "Development"


class ExecutionEngine(RQASubMatricesCarryover,
                      BaseRunnable):
    """
    Execution engine for conducting recurrence quantification analysis (RQA).

    :ivar settings: Settings.
    :ivar opencl: OpenCL environment.
    :ivar verbose: Should additional information should be provided during conducting the computations?
    :ivar edge_length: Default edge length of the sub matrices.
    :ivar processing_order: Processing order of the sub matrices.
    :ivar selector: Flavour selection approach.
    :ivar matrix_representation: Representation of the sub matrices.
    :ivar variants: List of RQA implementation variants.
    :ivar use_profiling_events_time: Should OpenCL profiling events used for time measurements?
    """

    def __init__(self,
                 settings,
                 opencl=None,
                 verbose=False,
                 edge_length=10240,
                 processing_order=Diagonal,
                 matrix_representation=MatrixRepresentation.Uncompressed,
                 selector=SingleSelector(loop_unroll_factors=(1,)),
                 variants=(ColumnMaterialisationUncompressedByteNoRecycling,),
                 variants_kwargs=None,
                 use_profiling_events_time=True):

        RQASubMatricesCarryover.__init__(self,
                                         settings,
                                         verbose,
                                         edge_length,
                                         processing_order)

        self.opencl = opencl

        self.matrix_representation = matrix_representation

        self.selector = selector
        self.variants = variants
        self.variants_kwargs = variants_kwargs if variants_kwargs else {}

        self.use_profiling_events_time = use_profiling_events_time

        self.matrix_runtimes = MatrixRuntimes(self.number_of_partitions)

        self.__initialise()

    def validate_opencl(self):
        """
        Validate OpenCL object handed over as a parameter in constructor.
        """
        if not self.opencl:
            self.opencl = OpenCL(verbose=self.verbose)

    def __initialise(self):
        """
        Initialise the compute device-specific global data structures.
        """

        self.validate_opencl()

        self.device_selector = {}

        self.device_vertical_frequency_distribution = {}
        self.device_white_vertical_frequency_distribution = {}
        self.device_diagonal_frequency_distribution = {}

        for device in self.opencl.devices:
            self.device_selector[device] = copy.deepcopy(self.selector)
            self.device_selector[device].setup(device,
                                               self.settings,
                                               self.opencl,
                                               self.variants,
                                               self.variants_kwargs)

            self.device_vertical_frequency_distribution[device] = self.get_empty_global_frequency_distribution()
            self.device_white_vertical_frequency_distribution[device] = self.get_empty_global_frequency_distribution()
            self.device_diagonal_frequency_distribution[device] = self.get_empty_global_frequency_distribution()

    def reset(self):
        """
        Reset the global data structures.
        """

        RQASubMatricesCarryover.reset(self)
        self.__initialise()

    def extend_sub_matrix(self,
                          sub_matrix):
        """
        Extend the sub matrix by related data from the global data structures.

        :param sub_matrix: Sub matrix to extend.
        """

        sub_matrix.recurrence_points = self.get_recurrence_points(sub_matrix)

        sub_matrix.vertical_length_carryover = self.get_vertical_length_carryover(sub_matrix)
        sub_matrix.white_vertical_length_carryover = self.get_white_vertical_length_carryover(sub_matrix)
        sub_matrix.diagonal_length_carryover = self.get_diagonal_length_carryover(sub_matrix)

        if self.matrix_representation != MatrixRepresentation.Uncompressed:
            sub_matrix.vertical_index_carryover = self.get_vertical_index_carryover(sub_matrix)
            sub_matrix.diagonal_index_carryover = self.get_diagonal_index_carryover(sub_matrix)

            sub_matrix.white_vertical_flag_carryover = self.get_white_vertical_flag_carryover(sub_matrix)

        sub_matrix.vertical_frequency_distribution = self.get_empty_local_frequency_distribution()
        sub_matrix.white_vertical_frequency_distribution = self.get_empty_local_frequency_distribution()
        sub_matrix.diagonal_frequency_distribution = self.get_empty_local_frequency_distribution()

    def update_global_data_structures(self,
                                      device,
                                      sub_matrix):
        """
        Update global data structures with values that are computed regarding a specific sub matrix.

        :param device: OpenCL device.
        :param sub_matrix: Sub matrix that has been analysed.
        """

        self.set_recurrence_points(sub_matrix)

        self.set_vertical_length_carryover(sub_matrix)
        self.set_white_vertical_length_carryover(sub_matrix)
        self.set_diagonal_length_carryover(sub_matrix)

        if self.matrix_representation != MatrixRepresentation.Uncompressed:
            self.set_vertical_index_carryover(sub_matrix)
            self.set_diagonal_index_carryover(sub_matrix)

            self.set_white_vertical_flag_carryover(sub_matrix)

        self.device_vertical_frequency_distribution[device] += sub_matrix.vertical_frequency_distribution
        self.device_white_vertical_frequency_distribution[device] += sub_matrix.white_vertical_frequency_distribution
        self.device_diagonal_frequency_distribution[device] += sub_matrix.diagonal_frequency_distribution

    def process_sub_matrix_queue(self,
                                 **kwargs):
        """
        Processing of a single sub matrix queue.
        A single queue refers to a specific sub matrix processing level.
        All sub matrices belonging to the same level can be processed simultaneously.

        :param kwargs: Keyword arguments.
        """
        device = kwargs['device']
        sub_matrix_queue = kwargs['sub_matrix_queue']

        while True:
            try:
                # Get sub matrix from queue
                sub_matrix = sub_matrix_queue.get(False)

                # Extend sub matrix
                self.extend_sub_matrix(sub_matrix)

                # Process sub matrix
                sub_matrix_processed = False
                flavour = None

                while not sub_matrix_processed:
                    flavour = self.device_selector[device].get_flavour()

                    try:
                        start_time = time.time()
                        flavour_runtimes = flavour.variant_instance.process_sub_matrix(sub_matrix)
                        end_time = time.time()

                        if not self.use_profiling_events_time:
                            flavour_runtimes = FlavourRuntimesMonolithic(execute_computations=end_time - start_time)

                        sub_matrix_processed = True
                        self.device_selector[device].increment_sub_matrix_count()
                    except SubMatrixNotProcessedException as error:
                        if self.device_selector[device].__class__ == SingleSelector:
                            self.print_out(error)
                            flavour_runtimes = FlavourRuntimesMonolithic()
                            break

                # Update flavour runtimes
                flavour.update_runtimes(sub_matrix,
                                        flavour_runtimes)

                # Update matrix runtimes
                self.matrix_runtimes.update_sub_matrix(sub_matrix,
                                                       flavour_runtimes)

                # Update global data structures
                self.update_global_data_structures(device,
                                                   sub_matrix)

            except queue.Empty:
                break

    def run_single_device(self):
        """
        Perform the computations using only a single OpenCL compute device.
        No seperate thread is launched.
        """

        for sub_matrix_queue in self.sub_matrix_queues:
            self.process_sub_matrix_queue(device=self.opencl.devices[0],
                                          sub_matrix_queue=sub_matrix_queue)

    def run_multiple_devices(self):
        """
        Perform the computations using multiple OpenCL compute devices.
        One thread per OpenCL compute device is launched.
        """

        for sub_matrix_queue in self.sub_matrix_queues:
            threads = []

            for device in self.opencl.devices:
                kwargs = {'device': device,
                          'sub_matrix_queue': sub_matrix_queue}

                thread = Thread(target=self.process_sub_matrix_queue,
                                kwargs=kwargs)

                thread.start()

                threads.append(thread)

            for thread in threads:
                thread.join()

    def run(self):
        """
        Execute the RQA computations.

        :return: RQA results.
        """

        self.reset()

        if not self.opencl.devices:
            print('No device specified!')
            return 0
        elif len(self.opencl.devices) == 1:
            self.run_single_device()
        elif len(self.opencl.devices) > 1:
            self.run_multiple_devices()

        self.post_process_length_carryovers()

        if self.matrix_representation == MatrixRepresentation.CSC:
            self.post_process_vertical_index_carryover()

        for device in self.opencl.devices:
            self.diagonal_frequency_distribution += self.device_diagonal_frequency_distribution[device]
            self.vertical_frequency_distribution += self.device_vertical_frequency_distribution[device]
            self.white_vertical_frequency_distribution += self.device_white_vertical_frequency_distribution[device]

        if self.settings.is_matrix_symmetric:
            self.extent_diagonal_frequency_distribution()

        return RQAResult(self.settings,
                         self.matrix_runtimes,
                         recurrence_points=self.recurrence_points,
                         diagonal_frequency_distribution=self.diagonal_frequency_distribution,
                         vertical_frequency_distribution=self.vertical_frequency_distribution,
                         white_vertical_frequency_distribution=self.white_vertical_frequency_distribution)
