#!/usr/bin/env python

"""
Custom exceptions.
"""

__author__ = "Tobias Rawald"
__copyright__ = "Copyright 2015, 2018 The PyRQA project"
__credits__ = ["Tobias Rawald",
               "Mike Sips"]
__license__ = "Apache-2.0"
__maintainer__ = "Tobias Rawald"
__email__ = "pyrqa@gmx.net"
__status__ = "Development"


class UnsupportedNeighbourhoodException(Exception):
    """
    Neighbourhood chosen is not supported.
    """


class UnsupportedMatrixRepresenationException(Exception):
    """
    Neighbourhood chosen is not supported.
    """


class UnsupportedTreeException(Exception):
    """
    Neighbourhood chosen is not supported.
    """


class NoOpenCLPlatformDetectedException(Exception):
    """
    No OpenCL platform could be detected.
    """


class NoOpenCLDeviceDetectedException(Exception):
    """
    No OpenCL device could be detected.
    """


class OpenCLPlatformIndexOutOfBoundsException(Exception):
    """
    OpenCL platform index is out of bounds.
    """


class OpenCLDeviceIndexOutOfBoundsException(Exception):
    """
    OpenCL device index is out of bounds.
    """


class NoOpenCLKernelFoundException(Exception):
    """
    No OpenCL kernel has been found.
    """


class SelectorNotFullySetupException(Exception):
    """
    No variant execption.
    """


class NoLoopUnrollException(Exception):
    """
    No loop unroll factor execption.
    """


class NoFlavorException(Exception):
    """
    No flavor execption.
    """


class NoSubMatrixRuntimesAvailableException(Exception):
    """
    No sub matrix runtimes are available.
    """


class SubMatrixNotProcessedException(Exception):
    """
    Sub matrix was not processed.
    """


class DeviceFissionNotSupportedException(Exception):
    """
    Device fission not support by OpenCL platform.
    """


class NoSubDevicePropertiesException(Exception):
    """
    No sub device properties are specified.
    """


class DeviatingNumberOfSubDevicePropertiesException(Exception):
    """
    Deviating number of sub device properties specified.
    """


class InvalidSubDevicePropertiesException(Exception):
    """
    Invalid sub device properties.
    """


class OpenCLSubDeviceIndexOutOfBoundsException(Exception):
    """
    OpenCL device index is out of bounds.
    """


class TimeDelayReconstructionNotSupportedException(Exception):
    """
    Time series class does not support recurrence vector reconstruction according to the time delay method.
    """


class UnsupportedDataTypeException(Exception):
    """
    Data type is unsupported.
    """
