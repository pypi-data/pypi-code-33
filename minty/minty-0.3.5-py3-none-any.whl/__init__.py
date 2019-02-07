import logging
import statsd


class Base:
    """Base class for other "minty" classes

    This base class provides lazy-loaded "self.logger" and "self.statsd"
    properties.
    """

    __slots__ = ["_logger", "_statsd"]

    @property
    def logger(self):
        """Return this object's logger instance, create one if necessary

        :return: A logger object for this instance
        :rtype: logging.Logger
        """
        try:
            self._logger
        except AttributeError:
            self._logger = logging.getLogger(self.__class__.__name__)

        return self._logger

    @property
    def statsd(self):
        """Return this object's statsd instance, create one if necessary

        :return: A statsd object for this instance
        :rtype: statsd.Client
        """
        try:
            self._statsd
        except AttributeError:
            self._statsd = statsd.Client(self.__class__.__name__)

        return self._statsd
