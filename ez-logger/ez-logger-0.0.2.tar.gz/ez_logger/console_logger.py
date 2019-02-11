import logging
from base_logger import BaseLogger


class ConsoleLogger(BaseLogger):
    """
    ConsoleLogger provides a logger that could be used for simple log messages to console.
    It uses colorlog formatter to color code log messages for different log levels.

    Parameters
    ----------
    name : `string`, `optional`
         Name of the logger.
    log_level : `string`, `optional`
         log_level
         Default value is info. Other allowed values are debug, warning, error or critical

    Examples
    --------
    >>> logger = ConsoleLogger()
    """

    def __init__(self, name=None, log_level='info'):
        super(ConsoleLogger, self).__init__(
            name=name,
            log_level=log_level
        )
        self.logger = self.__getLogger()

    def __getLogger(self):
        # Create a logger object
        logger = logging.getLogger(
            name=self._get_logger_name()
        )

        # Set the log level
        logger.setLevel(self._get_log_level())

        # Add console handler
        logger.addHandler(self._get_console_handler())
        return logger
