"""Exceptions thrown by limit function call implementations.

Adapted from https://github.com/sfalkner/pynisher
"""
from automl.client.core.common import constants


class CpuTimeoutException(Exception):
    """Exception to raise when the cpu time exceeded."""

    def __init__(self):
        """Constructor."""
        super(CpuTimeoutException, self).__init__(
            constants.ClientErrors.EXCEEDED_TIME_CPU)


class TimeoutException(Exception):
    """Exception to raise when the total execution time exceeded."""

    def __init__(self, value=None):
        """Constructor.

        :param value: time consumed
        """
        super(TimeoutException, self).__init__(
            constants.ClientErrors.EXCEEDED_TIME)
        self.value = value


class MemorylimitException(Exception):
    """Exception to raise when memory exceeded."""

    def __init__(self, value=None):
        """Constructor.

        :param value:  the memory consumed.
        """
        super(MemorylimitException, self).__init__(
            constants.ClientErrors.EXCEEDED_MEMORY)
        self.value = value


class SubprocessException(Exception):
    """Exception to raise when subprocess terminated."""

    def __init__(self, message=None):
        """Constructor.

        :param value:  Exception message.
        """
        if message is None:
            super(SubprocessException, self).__init__(
                constants.ClientErrors.SUBPROCESS_ERROR)
        else:
            super(SubprocessException, self).__init__(message)


class AnythingException(Exception):
    """Exception to raise for all other exceptions."""

    def __init__(self, message=None):
        """Constructor."""
        if message is None:
            super(AnythingException, self).__init__(
                constants.ClientErrors.GENERIC_ERROR)
        else:
            super(AnythingException, self).__init__(message)
