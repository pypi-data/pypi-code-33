#!/usr/bin/env python

"""
Detect diagonal lines.

Input data format: Row store
Recurrence matrix materialisation: No
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
                          sub_matrix,
                          device,
                          context,
                          command_queue,
                          kernels,
                          vectors_x_buffer=None,
                          vectors_y_buffer=None):
    """
    :param settings: Settings.
    :param sub_matrix: Sub matrix.
    :param device: OpenCL device.
    :param context: OpenCL context.
    :param command_queue: OpenCL command queue.
    :param kernels: OpenCL kernels.
    :param vectors_x_buffer: OpenCL vectors buffer X dimension.
    :param vectors_y_buffer: OpenCL vectors buffer Y dimension.
    :return: Runtimes.
    """
    transfer_to_device_events = []
    execute_computations_events = []
    transfer_from_device_events = []

    detect_diagonal_lines_kernel = kernels[0]

    # Write to buffers
    if vectors_x_buffer is None:
        vectors_x = settings.time_series.get_vectors(sub_matrix.start_x,
                                                     sub_matrix.dim_x)

        vectors_x_buffer = cl.Buffer(context,
                                     cl.mem_flags.READ_ONLY,
                                     vectors_x.nbytes)

        transfer_to_device_events.append(cl.enqueue_copy(command_queue,
                                                         vectors_x_buffer,
                                                         vectors_x,
                                                         device_offset=0,
                                                         wait_for=None,
                                                         is_blocking=False))

    if vectors_y_buffer is None:
        vectors_y = settings.time_series.get_vectors(sub_matrix.start_y,
                                                     sub_matrix.dim_y)

        vectors_y_buffer = cl.Buffer(context,
                                     cl.mem_flags.READ_ONLY,
                                     vectors_y.nbytes)

        transfer_to_device_events.append(cl.enqueue_copy(command_queue,
                                                         vectors_y_buffer,
                                                         vectors_y,
                                                         device_offset=0,
                                                         wait_for=None,
                                                         is_blocking=False))

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

    # Detect diagonal lines kernel
    if settings.is_matrix_symmetric:
        detect_diagonal_lines_args = [vectors_x_buffer,
                                      vectors_y_buffer,
                                      np.uint32(sub_matrix.dim_x),
                                      np.uint32(sub_matrix.dim_y),
                                      np.uint32(sub_matrix.start_x),
                                      np.uint32(sub_matrix.start_y),
                                      np.uint32(settings.time_series.embedding_dimension),
                                      settings.radius,
                                      np.uint32(settings.theiler_corrector),
                                      np.uint32(sub_matrix.diagonal_offset),
                                      diagonal_frequency_distribution_buffer,
                                      diagonal_carryover_buffer]

        global_work_size = [int(sub_matrix.dim_x + (device.max_work_group_size - (sub_matrix.dim_x % device.max_work_group_size)))]

    else:
        detect_diagonal_lines_args = [vectors_x_buffer,
                                      vectors_y_buffer,
                                      np.uint32(sub_matrix.dim_x + sub_matrix.dim_y - 1),
                                      np.uint32(sub_matrix.dim_y),
                                      np.uint32(sub_matrix.start_x),
                                      np.uint32(sub_matrix.start_y),
                                      np.uint32(settings.embedding_dimension),
                                      settings.radius,
                                      np.uint32(settings.theiler_corrector),
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
