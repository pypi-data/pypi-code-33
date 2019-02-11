"""Exceptions thrown by limit function call implementations.

Adapted from https://github.com/sfalkner/pynisher
"""
from automl.client.core.common import constants
from automl.client.core.common.exceptions import ClientException


# TODO: We need to change how exception handling works during training, then change exception type to user


class AutoMLRuntimeException(ClientException):
    """Exception to raise for all other exceptions."""

    def __init__(self, message=None):
        """Constructor.

        :param message:  Exception message.
        """
        if message is None:
            super(AutoMLRuntimeException, self).__init__(
                constants.ClientErrors.GENERIC_ERROR)
        else:
            super(AutoMLRuntimeException, self).__init__(message)


class CpuTimeoutException(AutoMLRuntimeException):
    """Exception to raise when the cpu time exceeded."""

    def __init__(self):
        """Constructor."""
        super(CpuTimeoutException, self).__init__(
            constants.ClientErrors.EXCEEDED_TIME_CPU)


class TimeoutException(AutoMLRuntimeException):
    """Exception to raise when the total execution time exceeded."""

    def __init__(self, value=None):
        """Constructor.

        :param value: time consumed
        """
        super(TimeoutException, self).__init__(
            constants.ClientErrors.EXCEEDED_TIME)
        self.value = value


class MemorylimitException(AutoMLRuntimeException):
    """Exception to raise when memory exceeded."""

    def __init__(self, value=None):
        """Constructor.

        :param value:  the memory consumed.
        """
        super(MemorylimitException, self).__init__(
            constants.ClientErrors.EXCEEDED_MEMORY)
        self.value = value


class SubprocessException(AutoMLRuntimeException):
    """Exception to raise when subprocess terminated."""

    def __init__(self, message=None):
        """Constructor.

        :param message:  Exception message.
        """
        if message is None:
            super(SubprocessException, self).__init__(
                constants.ClientErrors.SUBPROCESS_ERROR)
        else:
            super(SubprocessException, self).__init__(message)
