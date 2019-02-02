#!/usr/bin/env python

"""
Conduct recurrence quantification analysis.

Input data representation: Column store
Recurrence matrix materialisation: Yes
Recurrence matrix representation: Uncompressed
Similarity value representation: Bit
Intermediate results recycling: Yes
"""

import numpy as np

from pyrqa.base_classes import BaseSettings
from pyrqa.operators.detect_diagonal_lines.materialisation_uncompressed_bit import detect_diagonal_lines
from pyrqa.operators.detect_vertical_lines.fixed_radius.column_materialisation_uncompressed_bit_recycling import \
    detect_vertical_lines
from pyrqa.runtimes import FlavourRuntimesMultipleOperators

__author__ = "Tobias Rawald"
__copyright__ = "Copyright 2015, 2018 The PyRQA project"
__credits__ = ["Tobias Rawald",
               "Mike Sips"]
__license__ = "Apache-2.0"
__maintainer__ = "Tobias Rawald"
__email__ = "pyrqa@gmx.net"
__status__ = "Development"


class ColumnMaterialisationUncompressedBitRecycling(BaseSettings):
    """
    See module description regarding computational properties.

    :ivar opencl: OpenCL environment.
    :ivar device: OpenCL device.
    :ivar data_type: Data type to represent the similarity values.
    :ivar optimisations_enabled: Are the default OpenCL compiler optimisations enabled?
    :ivar loop_unroll: Loop unrolling factor.
    :ivar program: OpenCL program.
    :ivar program_created: Has the OpenCL program already been created?
    :ivar kernels: OpenCL kernels.
    :ivar kernels_created: Have the OpenCL kernels already been created?
    """

    def __init__(self,
                 settings,
                 opencl,
                 device,
                 **kwargs):
        """
        :param settings: Settings.
        :param opencl: OpenCL environment.
        :param device: OpenCL device.
        :param kwargs: Keyword arguments.
        """

        BaseSettings.__init__(self,
                              settings)

        self.opencl = opencl
        self.device = device

        self.data_type = kwargs['data_type'] if 'data_type' in list(kwargs.keys()) else np.uint32
        self.optimisations_enabled = kwargs['optimisations_enabled'] if 'optimisations_enabled' in list(kwargs.keys()) else False
        self.loop_unroll = kwargs['loop_unroll'] if 'loop_unroll' in list(kwargs.keys()) else 1

        self.program = None
        self.program_created = False

        self.kernels = {}
        self.kernels_created = False

        self.__initialize()

    def __initialize(self):
        """
        Initialization of the variant.
        """
        if not self.program_created:
            self.program = self.opencl.create_program(self.device,
                                                      (detect_vertical_lines,
                                                       detect_diagonal_lines),
                                                      self.settings.kernels_sub_dir,
                                                      self.settings.time_series.data.dtype,
                                                      optimisations_enabled=self.optimisations_enabled,
                                                      loop_unroll=self.loop_unroll)

            self.program_created = True

        if not self.kernels_created:
            self.kernels = self.opencl.create_kernels(self.program,
                                                      (self.settings.clear_buffer_kernel_name(self.data_type),
                                                       'detect_vertical_lines',
                                                       self.settings.diagonal_kernel_name))

            self.kernels_created = True

    def process_sub_matrix(self,
                           sub_matrix):
        """
        Processing of a single sub matrix.

        :param sub_matrix: Sub matrix.
        :return: Runtimes for processing the sub matrix.
        """
        # Create variant runtimes
        variant_runtimes = FlavourRuntimesMultipleOperators()

        # Detect vertical lines
        sub_matrix_buffer, \
            detect_vertical_lines_runtimes = detect_vertical_lines(self.settings,
                                                                   self.data_type,
                                                                   sub_matrix,
                                                                   self.device,
                                                                   self.opencl.contexts[self.device],
                                                                   self.opencl.command_queues[self.device],
                                                                   (self.kernels[self.settings.clear_buffer_kernel_name(self.data_type)],
                                                                    self.kernels['detect_vertical_lines']))

        variant_runtimes.detect_vertical_lines_runtimes = detect_vertical_lines_runtimes

        # Detect diagonal lines
        detect_diagonal_lines_runtimes = detect_diagonal_lines(self.settings,
                                                               self.data_type,
                                                               sub_matrix,
                                                               sub_matrix_buffer,
                                                               self.device,
                                                               self.opencl.contexts[self.device],
                                                               self.opencl.command_queues[self.device],
                                                               (self.kernels[self.settings.diagonal_kernel_name],))

        variant_runtimes.detect_diagonal_lines_runtimes = detect_diagonal_lines_runtimes

        return variant_runtimes
