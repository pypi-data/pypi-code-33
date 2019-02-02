#!/usr/bin/env python

"""
Detect diagonal lines.

Recurrence matrix representation: Uncompressed
Similarity value representation: Bit
"""

import numpy as np
import pyopencl as cl

from pyrqa.opencl import OpenCL
from pyrqa.runtimes import OperatorRuntimes

__author__ = "Tobias Rawald"
__copyright__ = "Copyright 2015, 2018 The PyRQA project"
__credits__ = ["Tobias Rawald",
               "Mike Sips"]
__license__ = "Apache-2.0"
__maintainer__ = "Tobias Rawald"
__email__ = "pyrqa@gmx.net"
__status__ = "Development"


def detect_diagonal_lines(settings,
                          data_type,
                          sub_matrix,
                          sub_matrix_buffer,
                          device,
                          context,
                          command_queue,
                          kernels):
    """
    :param settings: Settings.
    :param data_type: Data type.
    :param sub_matrix: Sub matrix.
    :param sub_matrix_buffer: Sub matrix buffer.
    :param device: OpenCL device.
    :param context: OpenCL context.
    :param command_queue: OpenCL command queue.
    :param kernels: OpenCL kernels.
    :return: Runtimes.
    """
    transfer_to_device_events = []
    execute_computations_events = []
    transfer_from_device_events = []

    detect_diagonal_lines_kernel = kernels[0]

    # Write to buffers
    diagonal_carryover_buffer = cl.Buffer(context,
                                          cl.mem_flags.READ_WRITE,
                                          sub_matrix.diagonal_length_carryover.nbytes)

    transfer_to_device_events.append(cl.enqueue_copy(command_queue,
                                                     diagonal_carryover_buffer,
                                                     sub_matrix.diagonal_length_carryover,
                                                     device_offset=0,
                                                     wait_for=None,
                                                     is_blocking=False))

    diagonal_frequency_distribution_buffer = cl.Buffer(context,
                                                       cl.mem_flags.READ_WRITE,
                                                       sub_matrix.diagonal_frequency_distribution.nbytes)

    transfer_to_device_events.append(cl.enqueue_copy(command_queue,
                                                     diagonal_frequency_distribution_buffer,
                                                     sub_matrix.diagonal_frequency_distribution,
                                                     device_offset=0,
                                                     wait_for=None,
                                                     is_blocking=False))

    command_queue.finish()

    # Execute detect diagonal lines kernel
    if settings.is_matrix_symmetric:
        detect_diagonal_lines_args = [sub_matrix_buffer,
                                      np.uint32(sub_matrix.dim_x),
                                      np.uint32(sub_matrix.dim_y),
                                      np.uint32(sub_matrix.start_x),
                                      np.uint32(sub_matrix.start_y),
                                      np.uint32(settings.theiler_corrector),
                                      np.uint32(sub_matrix.bits_per_element(data_type)),
                                      np.uint32(sub_matrix.diagonal_offset),
                                      diagonal_frequency_distribution_buffer,
                                      diagonal_carryover_buffer]

        global_work_size = [int(sub_matrix.dim_x + (device.max_work_group_size - (sub_matrix.dim_x % device.max_work_group_size)))]

    else:
        detect_diagonal_lines_args = [sub_matrix_buffer,
                                      np.uint32(sub_matrix.dim_x),
                                      np.uint32(sub_matrix.dim_y),
                                      np.uint32(sub_matrix.dim_x + sub_matrix.dim_y - 1),
                                      np.uint32(sub_matrix.start_x),
                                      np.uint32(sub_matrix.start_y),
                                      np.uint32(settings.theiler_corrector),
                                      np.uint32(sub_matrix.bits_per_element(data_type)),
                                      diagonal_frequency_distribution_buffer,
                                      diagonal_carryover_buffer]

        global_work_size_x = sub_matrix.dim_x + sub_matrix.dim_y - 1
        global_work_size = [int(global_work_size_x + (device.max_work_group_size - (global_work_size_x % device.max_work_group_size)))]

    OpenCL.set_kernel_args(detect_diagonal_lines_kernel,
                           detect_diagonal_lines_args)

    local_work_size = None

    execute_computations_events.append(cl.enqueue_nd_range_kernel(command_queue,
                                                                  detect_diagonal_lines_kernel,
                                                                  global_work_size,
                                                                  local_work_size))

    command_queue.finish()

    # Read from buffers
    transfer_from_device_events.append(cl.enqueue_copy(command_queue,
                                                       sub_matrix.diagonal_length_carryover,
                                                       diagonal_carryover_buffer,
                                                       device_offset=0,
                                                       wait_for=None,
                                                       is_blocking=False))

    transfer_from_device_events.append(cl.enqueue_copy(command_queue,
                                                       sub_matrix.diagonal_frequency_distribution,
                                                       diagonal_frequency_distribution_buffer,
                                                       device_offset=0,
                                                       wait_for=None,
                                                       is_blocking=False))

    command_queue.finish()

    # Determine runtimes
    runtimes = OperatorRuntimes()
    runtimes.transfer_to_device += OpenCL.convert_events_runtime(transfer_to_device_events)
    runtimes.execute_computations += OpenCL.convert_events_runtime(execute_computations_events)
    runtimes.transfer_from_device += OpenCL.convert_events_runtime(transfer_from_device_events)

    return runtimes
