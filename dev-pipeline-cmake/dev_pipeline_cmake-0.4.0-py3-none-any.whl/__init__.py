#!/usr/bin/python3

"""This modules supports building CMake projects."""

import devpipeline_cmake.cmake


def make_cmake(current_configuration):
    """
    Construct a builder that works with CMake.

    Arguments
    current_configuration - configuration for the current target
    common_wrapper - a function to provide integration with built-in
                     functionality
    """
    # pylint: disable=protected-access
    return devpipeline_cmake.cmake._make_cmake(current_configuration)


_MAJOR = 0
_MINOR = 4
_PATCH = 0

_STRING = "{}.{}.{}".format(_MAJOR, _MINOR, _PATCH)

_CMAKE_TOOL = (make_cmake, "({}) CMake build system generator.".format(_STRING))
