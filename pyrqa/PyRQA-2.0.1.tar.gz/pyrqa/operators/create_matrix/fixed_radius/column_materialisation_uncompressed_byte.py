#!/usr/bin/env python

"""
Create recurrence matrix using brute-force processing.

Input data format: Column store
Recurrence matrix materialisation: Yes
Recurrence matrix representation: Uncompressed
Similarity value representation: Byte
"""

import numpy as np
import pyopencl as cl

from pyrqa.exceptions import SubMatrixNotProcessedException
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


def create_matrix(settings,
                  data_type,
                  sub_matrix,
                  device,
                  context,
                  command_queue,
                  kernels,
                  return_sub_matrix_data=False):
    """
    :param settings: Settings.
    :param data_type: Data type.
    :param sub_matrix: Sub matrix.
    :param device: OpenCL device.
    :param context: OpenCL context.
    :param command_queue: OpenCL command queue.
    :param kernels: OpenCL kernels.
    :param return_sub_matrix_data: Shall the sub matrix data be returned?
    :return: return_sub_matrix_data==False: OpenCL sub matrix buffer, runtimes / return_sub_matrix_data==True: Sub matrix data, runtimes.
    """
    transfer_to_device_events = []
    execute_computations_events = []
    transfer_from_device_events = []

    create_matrix_kernel = kernels[0]

    # Write to buffers
    time_series_x = settings.time_series.get_time_series(sub_matrix.start_x,
                                                         sub_matrix.dim_x)

    time_series_x_buffer = cl.Buffer(context,
                                     cl.mem_flags.READ_ONLY,
                                     time_series_x.nbytes)

    transfer_to_device_events.append(cl.enqueue_copy(command_queue,
                                                     time_series_x_buffer,
                                                     time_series_x,
                                                     device_offset=0,
                                                     wait_for=None,
                                                     is_blocking=False))

    time_series_y = settings.time_series.get_time_series(sub_matrix.start_y,
                                                         sub_matrix.dim_y)

    time_series_y_buffer = cl.Buffer(context,
                                     cl.mem_flags.READ_ONLY,
                                     time_series_y.nbytes)

    transfer_to_device_events.append(cl.enqueue_copy(command_queue,
                                                     time_series_y_buffer,
                                                     time_series_y,
                                                     device_offset=0,
                                                     wait_for=None,
                                                     is_blocking=False))

    if sub_matrix.size_byte(data_type) > device.max_mem_alloc_size:
        raise SubMatrixNotProcessedException("Calculation aborted: The size of the sub matrix is too large.")

    sub_matrix_buffer = cl.Buffer(context,
                                  cl.mem_flags.READ_WRITE,
                                  int(sub_matrix.size_byte(data_type)))

    command_queue.finish()

    # Execute create matrix kernel
    create_matrix_args = [time_series_x_buffer,
                          time_series_y_buffer,
                          np.uint32(sub_matrix.dim_x),
                          np.uint32(settings.time_series.embedding_dimension),
                          np.uint32(settings.time_series.time_delay),
                          settings.radius,
                          sub_matrix_buffer]

    OpenCL.set_kernel_args(create_matrix_kernel,
                           create_matrix_args)

    global_work_size = [int(sub_matrix.dim_x + (device.max_work_group_size - (sub_matrix.dim_x % device.max_work_group_size))),
                        int(sub_matrix.dim_y)]

    local_work_size = None

    execute_computations_events.append(cl.enqueue_nd_range_kernel(command_queue,
                                                                  create_matrix_kernel,
                                                                  global_work_size,
                                                                  local_work_size))

    command_queue.finish()

    if return_sub_matrix_data:
        # Read from buffer
        sub_matrix.set_empty_data_byte(data_type)

        transfer_from_device_events.append(cl.enqueue_copy(command_queue,
                                                           sub_matrix.data,
                                                           sub_matrix_buffer,
                                                           device_offset=0,
                                                           wait_for=None,
                                                           is_blocking=False))

        command_queue.finish()

    runtimes = OperatorRuntimes()
    runtimes.transfer_to_device += OpenCL.convert_events_runtime(transfer_to_device_events)
    runtimes.execute_computations += OpenCL.convert_events_runtime(execute_computations_events)
    runtimes.transfer_from_device += OpenCL.convert_events_runtime(transfer_from_device_events)

    return sub_matrix_buffer, \
        runtimes
