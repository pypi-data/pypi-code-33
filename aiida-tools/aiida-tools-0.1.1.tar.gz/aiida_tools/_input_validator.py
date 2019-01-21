# -*- coding: utf-8 -*-

# © 2017-2019, ETH Zurich, Institut für Theoretische Physik
# Author: Dominik Gresch <greschd@gmx.ch>


from aiida.common.exceptions import InputValidationError

__all__ = ['get_input_validator']

def get_input_validator(inputdict):
    """
    Returns a function which validates and returns a given input.

    :param inputdict: Inputs to the calculation.
    :type inputdict: dict

    Parameters to the returned validator function:

    :param name: Name of the input.
    :type name: str

    :param valid_types: Valid types for the input value.
    :type valid_types: type, or tuple(type)

    :param required: Indicates whether the input is required. The default is ``True``.
    :type required: bool

    :param default: Default value that is returned if the value is not given, and not required.
    """
    def _validate_input(name, valid_types, required=True, default=None):
        try:
            value = inputdict.pop(name)
        except KeyError:
            if required:
                raise InputValidationError("Missing required input parameter '{}'".format(name))
            else:
                value = default

        if not isinstance(valid_types, (list, tuple)):
            valid_types = [valid_types]
        if not required:
            valid_types = list(valid_types) + [type(default)]
        valid_types = tuple(valid_types)

        if not isinstance(value, valid_types):
            raise InputValidationError("Input parameter '{}' is of type '{}', but should be of type(s) '{}'".format(name, type(value), valid_types))
        return value

    return _validate_input
