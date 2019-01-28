# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Activity-based loggers."""
from abc import ABC, abstractmethod
import contextlib


class ActivityLogger(ABC):
    """Abstract base class for activity loggers."""

    @abstractmethod
    def _log_activity(self, logger, activity_name, activity_type, custom_dimensions=None):
        """
        Log activity - should be overridden by subclasses with a proper implementation.

        :param logger:
        :param activity_name:
        :param activity_type:
        :param custom_dimensions:
        :return:
        """
        raise NotImplementedError

    @contextlib.contextmanager
    def log_activity(self, logger, activity_name, activity_type=None, custom_dimensions=None):
        """
        Log an activity using the given logger.

        :param logger:
        :param activity_name:
        :param activity_type:
        :param custom_dimensions:
        :return:
        """
        return self._log_activity(logger, activity_name, activity_type, custom_dimensions)


class DummyActivityLogger(ActivityLogger):
    """Dummy activity logger."""

    def _log_activity(self, logger, activity_name, activity_type, custom_dimensions=None):
        """
        Do nothing.

        :param logger:
        :param activity_name:
        :param activity_type:
        :param custom_dimensions:
        """
        yield None
