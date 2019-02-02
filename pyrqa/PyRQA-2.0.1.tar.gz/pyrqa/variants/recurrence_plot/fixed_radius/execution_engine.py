#!/usr/bin/env python

"""
Execution engine for creating recurrence plots.
"""

import copy
import sys
import time

from threading import Thread

from pyrqa.variants.recurrence_plot.fixed_radius.column_materialisation_uncompressed_byte import ColumnMaterialisationUncompressedByte
from ....base_classes import BaseRunnable
from ....exceptions import SubMatrixNotProcessedException
from ....opencl import OpenCL
from ....processing_order import Diagonal
from ....recurrence_analysis import RecurrencePlotSubMatrices
from ....result import RPResult
from ....runtimes import MatrixRuntimes, \
    FlavourRuntimesMonolithic
from ....selector import SingleSelector

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


class ExecutionEngine(RecurrencePlotSubMatrices,
                      BaseRunnable):
    """
    Execution engine.

    :ivar opencl: OpenCL environment.
    :ivar selector: Selector for flavour selection.
    :ivar variants: Variants from which flavours are created.
    :ivar use_profiling_events_time: Should the time measurements of the OpenCL profiling events be employed?
    :ivar matrix_runtimes: Runtimes for each sub matrix of the total recurrence matrix.
    """

    def __init__(self,
                 settings,
                 opencl=None,
                 verbose=False,
                 edge_length=10240,
                 processing_order=Diagonal,
                 selector=SingleSelector(loop_unroll_factors=(1,)),
                 variants=(ColumnMaterialisationUncompressedByte,),
                 variants_kwargs=None,
                 use_profiling_events_time=True):
        """
        :param settings: Settings.
        :param opencl: OpenCL environment.
        :param verbose: Should there be detailed outputs.
        :param edge_length: Sub matrix edge length.
        :param processing_order: Processing order of the sub matrices.
        :param selector: Selector for flavour selection.
        :param variants: Variants from which flavours are created.
        :param use_profiling_events_time: Should the time measurements of the OpenCL profiling events be employed?
        """

        RecurrencePlotSubMatrices.__init__(self,
                                           settings,
                                           verbose,
                                           edge_length,
                                           processing_order)

        self.opencl = opencl

        self.selector = selector
        self.variants = variants
        self.variants_kwargs = variants_kwargs if variants_kwargs else {}

        self.use_profiling_events_time = use_profiling_events_time

        self.matrix_runtimes = MatrixRuntimes(self.number_of_partitions)

        self.__initialise()

    def __initialise(self):
        """
        Initialise the compute device-specific global data structures.
        """

        self.validate_opencl()

        self.device_selector = {}

        for device in self.opencl.devices:
            self.device_selector[device] = copy.deepcopy(self.selector)
            self.device_selector[device].setup(device,
                                               self.settings,
                                               self.opencl,
                                               self.variants,
                                               self.variants_kwargs)

    def reset(self):
        """
        Reset the global data structures.
        """

        RecurrencePlotSubMatrices.reset(self)
        self.__initialise()

    def validate_opencl(self):
        """
        Validate OpenCL object handed over as a parameter in constructor.
        """
        if not self.opencl:
            self.opencl = OpenCL(verbose=self.verbose)

    def update_global_data_structures(self,
                                      sub_matrix):
        """
        Update the global data structures, in particular the recurrence matrix.

        :param sub_matrix: Sub matrix.
        """
        self.set_sub_matrix_data(sub_matrix)

    def process_sub_matrix_queue(self,
                                 **kwargs):
        """
        Process a single sub matrix queue.

        :param kwargs: Keyword arguments.
        """
        device = kwargs['device']
        sub_matrix_queue = kwargs['sub_matrix_queue']

        while True:
            try:
                # Get sub matrix from queue
                sub_matrix = sub_matrix_queue.get(False)

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
                self.update_global_data_structures(sub_matrix)

            except queue.Empty:
                break

    def run_single_device(self):
        for sub_matrix_queue in self.sub_matrix_queues:
            self.process_sub_matrix_queue(device=self.opencl.devices[0],
                                          sub_matrix_queue=sub_matrix_queue)

    def run_multiple_devices(self):
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
        self.reset()

        if not self.opencl.devices:
            print('No device specified!')
            return 0
        elif len(self.opencl.devices) == 1:
            self.run_single_device()
        elif len(self.opencl.devices) > 1:
            self.run_multiple_devices()

        return RPResult(self.settings,
                        self.matrix_runtimes,
                        recurrence_matrix=self.recurrence_matrix)
