#!/usr/bin/env python

"""
OpenCL
"""

import math
import os
import sys

import numpy as np
import pyopencl as cl

from mako.template import Template

from pyrqa.base_classes import BaseVerbose
from pyrqa.exceptions import NoOpenCLPlatformDetectedException, \
    NoOpenCLDeviceDetectedException, \
    OpenCLPlatformIndexOutOfBoundsException, \
    OpenCLDeviceIndexOutOfBoundsException, \
    NoOpenCLKernelFoundException, \
    DeviceFissionNotSupportedException, \
    NoSubDevicePropertiesException, \
    DeviatingNumberOfSubDevicePropertiesException, \
    InvalidSubDevicePropertiesException, \
    OpenCLSubDeviceIndexOutOfBoundsException, \
    UnsupportedDataTypeException

from .file_reader import FileReader

__author__ = "Tobias Rawald"
__copyright__ = "Copyright 2015, 2018 The PyRQA project"
__credits__ = ["Tobias Rawald",
               "Mike Sips"]
__license__ = "Apache-2.0"
__maintainer__ = "Tobias Rawald"
__email__ = "pyrqa@gmx.net"
__status__ = "Development"

DTYPE_TO_OPENCL_TYPE_MAPPING = {np.dtype('float16'): 'half',
                                np.dtype('float32'): 'float',
                                np.dtype('float64'): 'double'}


class OpenCL(BaseVerbose):
    """
    OpenCL environment.

    :ivar verbose: Verbosity of print out messages.
    :ivar command_line: Is the creation of the OpenCL environment conducted via command line?
    :ivar platform_id: ID of OpenCL platform to be used for execution.
    :ivar device_ids: IDs of OpenCL devices to be used for execution.
    :ivar config_file_path: Path to config file.
    :ivar enable_device_fission: Is the fission of device enabled?
    :ivar sub_device_properties: Properties of the sub devices.
    :ivar sub_device_ids: IDs of the sub devices.
    """

    def __init__(self,
                 verbose=False,
                 command_line=False,
                 platform_id=0,
                 device_ids=(0,),
                 config_file_path=os.path.join(os.path.dirname(os.path.relpath(__file__)), "config.ini"),
                 enable_device_fission=False,
                 sub_device_properties=None,
                 sub_device_ids=None):
        BaseVerbose.__init__(self,
                             verbose)

        self.command_line = command_line
        self.platform_id = platform_id
        self.device_ids = device_ids
        self.config_file_path = config_file_path

        self.enable_device_fission = enable_device_fission
        self.sub_device_properties = sub_device_properties
        self.sub_device_ids = sub_device_ids

        self.__initialise()

    def __initialise(self):
        """
        Initialise the instance variables.
        """

        self.platform = None
        self.devices = None
        self.contexts = {}
        self.command_queues = {}

        if self.command_line:
            self.create_environment_command_line()
        else:
            self.create_environment()

    def reset(self):
        """
        Reset the instance variables.
        """

        self.__initialise()

    @staticmethod
    def get_clear_buffer_kernel_sources(kernel_file_name='clear_buffer.cl'):
        """
        Get the sources of the clear buffer kernel.

        :param kernel_file_name: Name of the clear buffer kernel file.
        :return: Clear buffer kernel sources.
        """
        kernel_base_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'kernels')
        kernel_file_path = os.path.join(kernel_base_dir, 'clear_buffer')

        try:
            return FileReader.file_as_string(kernel_file_path, kernel_file_name)
        except IOError:
            raise NoOpenCLKernelFoundException(
                "Kernel with file name '%s' not found in path '%s'." % (kernel_file_name,
                                                                        kernel_file_path))

    def get_kernel_sources(self,
                           operator,
                           settings_sub_dir):
        """
        Get the kernel sources for a specific analytical operator.

        :param operator: Operator.
        :param settings_sub_dir: Kernel sub directory based on the similarity measure applied.
        :return: Operator kernel sources.
        """

        kernel_base_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'kernels')
        kernel_file_path = os.path.join(kernel_base_dir, *operator.__module__.split('.')[2:-1])
        kernel_file_name = self.get_kernel_file_name(operator)

        try:
            return FileReader.file_as_string(kernel_file_path, kernel_file_name)
        except IOError:
            kernel_file_path = os.path.join(kernel_file_path,
                                            settings_sub_dir)

            try:
                return FileReader.file_as_string(kernel_file_path, kernel_file_name)
            except IOError:
                raise NoOpenCLKernelFoundException(
                    "Kernel with file name '%s' not found in path '%s'." % (kernel_file_name,
                                                                            kernel_file_path))

    def get_kernel_file_name(self,
                             operator):
        """
        Get the kernel file name for a specific analytical operator.

        :param operator: Opertator.
        :return: Operator kernel file name.
        """

        if sys.version_info.major == 2:
            import ConfigParser
            config = ConfigParser.ConfigParser()
            config.read(self.config_file_path)
            return config.get('OperatorToKernelFileMapping', operator.__module__)
        elif sys.version_info.major == 3:
            import configparser
            config = configparser.ConfigParser()
            config.read(self.config_file_path)
            return config['OperatorToKernelFileMapping'][operator.__module__]

    @staticmethod
    def fill_program_source_template(program_source_template,
                                     dtype):
        """
        Fill program source template based on Mako (see https://www.makotemplates.org/).

        :param program_source_template: Program source template.
        :param dtype: Data type of floating point values.
        :return: Program source.
        """

        return Template(program_source_template).render(fp_type=DTYPE_TO_OPENCL_TYPE_MAPPING[dtype])

    @staticmethod
    def floating_point_data_type_supported(device,
                                           dtype):
        """
        Check whether the floating point chosen is supported by the device.

        :param device: OpenCL device.
        :param dtype: Floating point data type.
        :return: Is floating point data type supported?
        """

        native_vector_width = None
        if DTYPE_TO_OPENCL_TYPE_MAPPING[dtype] == 'half':
            native_vector_width = device.native_vector_width_half
        elif DTYPE_TO_OPENCL_TYPE_MAPPING[dtype] == 'float':
            native_vector_width = device.native_vector_width_float
        elif DTYPE_TO_OPENCL_TYPE_MAPPING[dtype] == 'double':
            native_vector_width = device.native_vector_width_double

        if native_vector_width is 0:
            return False

        return True

    def create_program(self,
                       device,
                       operators,
                       settings_sub_dir,
                       dtype,
                       optimisations_enabled=False,
                       loop_unroll=1):
        """
        Create OpenCL program.

        :param device: OpenCL device.
        :param operators: List of names of analytical operators.
        :param settings_sub_dir: Settings sub directory.
        :param dtype: Data type of floating point values.
        :param optimisations_enabled: Are OpenCL default compiler optimisations enabled?
        :param loop_unroll: Loop unrolling factor.
        :return: Program.
        """

        if not self.floating_point_data_type_supported(device,
                                                       dtype):
            raise UnsupportedDataTypeException("The data type '%s' is not supported by the OpenCL device." % DTYPE_TO_OPENCL_TYPE_MAPPING[dtype])

        if self.verbose:
            os.environ['PYOPENCL_COMPILER_OUTPUT'] = '1'
        else:
            os.environ['PYOPENCL_COMPILER_OUTPUT'] = '0'

        program_source = OpenCL.get_clear_buffer_kernel_sources()

        for operator in operators:
            program_source_template = self.get_kernel_sources(operator,
                                                              settings_sub_dir)

            program_source += self.fill_program_source_template(program_source_template,
                                                                dtype)

        program = cl.Program(self.contexts[device], program_source)
        options = ["-Dloop_unroll=%d" % loop_unroll]

        if not optimisations_enabled:
            options.append("-cl-opt-disable")

        program.build(options=options)

        return program

    def create_contexts(self):
        """
        Create OpenCL contexts for each OpenCL device.
        """

        for device in self.devices:
            self.print_out(OpenCL.get_device_info(device))

            context = cl.Context(devices=[device])
            self.contexts[device] = context

            command_queue = cl.CommandQueue(context, properties=cl.command_queue_properties.PROFILING_ENABLE)
            self.command_queues[device] = command_queue

    def create_environment(self):
        """
        Create OpenCL environment.
        """

        self.set_platform()
        self.print_out(OpenCL.get_platform_info(self.platform))

        self.set_devices()
        self.create_contexts()

    def create_environment_command_line(self):
        """
        Create OpenCL environment from command line.
        """

        platforms = cl.get_platforms()

        if platforms:
            platform_strings = []

            for platform_idx in np.arange(len(platforms)):
                platform_strings.append("[%d] %s" % (platform_idx, platforms[platform_idx]))

            platform_select = None
            if sys.version_info.major == 2:
                platform_select = int(raw_input("\nAvailable platform(s):\n%s\n\nChoose platform, e.g., '0': " % "\n".join(platform_strings)))
            if sys.version_info.major == 3:
                platform_select = int(input("\nAvailable platform(s):\n%s\n\nChoose platform, e.g., '0': " % "\n".join(platform_strings)))

            if platform_select not in np.arange(len(platforms)):
                raise OpenCLPlatformIndexOutOfBoundsException("Platform index '%d' is out of bounds." % platform_select)

            self.platform = platforms[platform_select]

            devices = self.platform.get_devices(cl.device_type.ALL)
            if devices:
                device_strings = []

                for device_idx in np.arange(len(devices)):
                    device_strings.append("[%d] %s" % (device_idx, devices[device_idx]))

                if sys.version_info.major == 2:
                    device_select = raw_input("\nAvailable device(s):\n%s\n\nChoose device(s), comma-separated, e.g., '0,1': " %
                                              "\n".join(device_strings))
                if sys.version_info.major == 3:
                    device_select = input("\nAvailable device(s):\n%s\n\nChoose device(s), comma-separated, e.g., '0,1': " %
                                          "\n".join(device_strings))

                device_indices = [int(x) for x in device_select.split(',')]

                self.devices = []

                for device_idx in device_indices:
                    if device_idx not in np.arange(len(devices)):
                        raise OpenCLDeviceIndexOutOfBoundsException("Device index '%d' is out of bounds.")
                    else:
                        self.devices.append(devices[device_idx])

                self.create_contexts()
            else:
                raise NoOpenCLDeviceDetectedException("No OpenCL device was detected.")
        else:
            raise NoOpenCLPlatformDetectedException("No OpenCL platform was detected.")

    @staticmethod
    def create_kernels(program,
                       kernel_names):
        """
        Create kernels.

        :param program: Program that contains the kernels.
        :param kernel_names: Names of kernels that should be created.
        :return: Dictionary mapping kernel names to kernels.
        """

        kernels = {}

        for kernel_name in kernel_names:
            kernels[kernel_name] = cl.Kernel(program, kernel_name)

        return kernels

    @staticmethod
    def convert_events_runtime(events):
        """
        Convert OpenCL events runtime to seconds.

        :param events: List of OpenCL events.
        :returns: Cumulated runtime in seconds.
        :rtype: Float value.
        """

        total = np.uint64(0)

        for event in events:
            total += event.get_profiling_info(cl.profiling_info.END) - event.get_profiling_info(cl.profiling_info.START)

        return np.float64(total) * math.pow(10, -9)

    @staticmethod
    def set_kernel_args(kernel,
                        args):
        """
        Set OpenCL kernel arguments.

        :param kernel: OpenCL kernel.
        :param args: Kernel arguments.
        """
        for idx in np.arange(len(args)):
            kernel.set_arg(int(idx), args[idx])

    def set_platform(self):
        """
        Set OpenCL platform.
        """

        try:
            platforms = cl.get_platforms()
        except cl.RuntimeError as error:
            error_str = "Could not find any platform: %s" % error
            print(error_str)

        if self.platform_id is not None:
            if self.platform_id in np.arange(len(platforms)):
                self.platform = platforms[self.platform_id]
            else:
                raise OpenCLPlatformIndexOutOfBoundsException("Platform with index '%d' could not be found." % self.platform_id)
        else:
            self.platform = platforms[0]

    @staticmethod
    def get_platform_info(platform):
        """
        Get OpenCL platform info.

        :param platform: OpenCL platform.
        :returns: OpenCL platform info.
        :rtype: String.
        """

        return "[Platform '%s']\n" % platform.name.strip() + \
               "Vendor: %s\n" % platform.vendor.strip() + \
               "Version: %s\n" % platform.version + \
               "Profile: %s\n" % platform.profile + \
               "Extensions: %s\n" % platform.extensions + \
               "\n"

    @staticmethod
    def get_device_ids_per_platform_id():
        """
        Get all compute device ids of all OpenCL platforms available mapped to the corresponding platform id.

        :return: Devices ids per platform id.
        """

        try:
            platforms = cl.get_platforms()
        except cl.RuntimeError as error:
            error_str = "Could not find any platform: %s" % error
            print(error_str)

        device_ids_per_platform_id = {}
        platform_id = 0
        for platform in platforms:
            device_ids_per_platform_id[platform_id] = np.arange(len(platform.get_devices()))
            platform_id += 1

        return device_ids_per_platform_id

    def set_devices(self):
        """
        Set OpenCL devices.
        """

        devices = self.platform.get_devices(cl.device_type.ALL)

        if not devices:
            raise NoOpenCLDeviceDetectedException("No OpenCL device could be detected.")

        if not self.enable_device_fission:
            self.devices = []
            for device_id in self.device_ids:
                if device_id not in np.arange(len(devices)):
                    raise OpenCLDeviceIndexOutOfBoundsException("Device with index '%d' could not be found." % device_id)

                self.devices.append(devices[device_id])
        else:
            opencl_version = self.platform.version[7:10]

            if opencl_version < '1.2':
                raise DeviceFissionNotSupportedException("Platform with OpenCL version '%s' does not support device fission." % opencl_version)
            elif not self.sub_device_properties:
                raise NoSubDevicePropertiesException("No sub device properties have been specified.")
            elif len(self.sub_device_properties) != len(self.device_ids):
                raise DeviatingNumberOfSubDevicePropertiesException(
                    "Number of sub device properties '%d' deviates from the number of device ids '%d'" %
                    (len(self.sub_device_properties), len(self.device_ids)))

            self.devices = []

            for idx in range(len(self.device_ids)):
                device_id = self.device_ids[idx]

                if device_id not in np.arange(len(devices)):
                    raise OpenCLDeviceIndexOutOfBoundsException("Device with index '%d' is out of bounds." % device_id)

                if not self.sub_device_properties[idx]:
                    raise InvalidSubDevicePropertiesException("Invalid sub device properties '%s'" % str(self.sub_device_properties[idx]))

                sub_devices = devices[device_id].create_sub_devices(self.sub_device_properties[idx])

                for sub_device_id in self.sub_device_ids[idx]:
                    if sub_device_id not in np.arange(len(sub_devices)):
                        raise OpenCLSubDeviceIndexOutOfBoundsException("Sub device index '%d' is out of bounds." % sub_device_id)

                    self.devices.append(sub_devices[sub_device_id])

    @staticmethod
    def get_device_info(device):
        """
        Get OpenCL device info.

        :param device: OpenCL device.
        :returns: Device info.
        :rtype: String.
        """
        return "[Device '%s']\n" % device.name.strip() + \
               "Vendor: %s\n" % device.vendor.strip() + \
               "Type: %s\n" % device.type + \
               "Version: %s\n" % device.version + \
               "Profile: %s\n" % device.profile + \
               "Max Clock Frequency: %s\n" % device.max_clock_frequency + \
               "Global Mem Size: %s\n" % device.global_mem_size + \
               "Address Bits: %s\n" % device.address_bits + \
               "Max Compute Units: %s\n" % device.max_compute_units + \
               "Max Work Group Size: %s\n" % device.max_work_group_size + \
               "Max Work Item Dimensions: %s\n" % device.max_work_item_dimensions + \
               "Max Work Item Sizes: %s\n" % device.max_work_item_sizes + \
               "Local Mem Size: %s\n" % device.local_mem_size + \
               "Max Mem Alloc Size: %s\n" % device.max_mem_alloc_size + \
               "Extensions: %s\n" % device.extensions + \
               "\n"
