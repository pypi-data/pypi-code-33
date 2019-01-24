"""
@Time    : 2019/1/16 17:56
@Author  : Sam
@Project : pyinfluxdb
@FileName: errors.py
@Software: PyCharm
@Blog    : https://blog.muumlover.com
"""
import sys


class PyInfluxError(Exception):
    """Base class for all PyMongo exceptions."""

    def __init__(self, message='', error_labels=None):
        super(PyInfluxError, self).__init__(message)
        self._message = message
        self._error_labels = set(error_labels or [])

    def has_error_label(self, label):
        """Return True if this error contains the given label.

        .. versionadded:: 3.7
        """
        return label in self._error_labels

    def _add_error_label(self, label):
        """Add the given label to this error."""
        self._error_labels.add(label)

    def _remove_error_label(self, label):
        """Remove the given label from this error."""
        self._error_labels.remove(label)

    def __str__(self):
        # if sys.version_info[0] == 2 and isinstance(self._message, unicode):
        if sys.version_info[0] == 2:
            return self._message.encode('utf-8', errors='replace')
        return str(self._message)


class ConfigurationError(PyInfluxError):
    """Raised when something is incorrectly configured.
    """
