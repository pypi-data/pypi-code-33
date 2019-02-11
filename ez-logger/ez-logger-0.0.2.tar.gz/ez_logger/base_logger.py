import logging
import colorlog


class BaseLogger(object):
    """
    BaseLogger is the parent class, that encapsulates the common functionality
    for different kinds of loggers.

    ConsoleLogger and FileLogger descend from BaseLogger

    Don't create BaseLogger objects. It is an abstract class. Use ConsoleLogger
    or FileLogger.
    """

    def __init__(self, name, log_level):
        self.name = name
        self.log_level = log_level

    def _get_logger_name(self):
        if self.name is None:
            return 'app'
        else:
            return self.name

    def _get_log_level(self):
        log_level_dict = {
            'info': logging.INFO,
            'debug': logging.DEBUG,
            'warning': logging.WARNING,
            'error': logging.ERROR,
            'critical': logging.CRITICAL
        }
        if self.log_level not in log_level_dict.keys():
            # wrong log_level specified, so defaulting to info.
            return logging.INFO
        else:
            return log_level_dict[self.log_level]

    def _get_console_handler(self):
        console_handler = logging.StreamHandler()
        console_formatter = colorlog.ColoredFormatter(
            '%(log_color)s%(message)s'
        )
        console_handler.setFormatter(console_formatter)
        return console_handler

    def __getLogger(self):
        """
        Returns the logger object. This method needs to be implemented
        by the child class
        """
        pass

    def info(self, message):
        """
        Writes info messages, these messages will only be written if
        log_level is set to debug or info.
        """
        self.logger.info(message)

    def error(self, message):
        """
        Writes error messages, these messages will only be written if
        log_level is set to debug, info, warning or error.
        """
        self.logger.error(message)

    def warning(self, message):
        """
        Writes warning messages, these messages will only be written
        if log_level is set to debug, info or warning.
        """
        self.logger.warning(message)

    def critical(self, message):
        """
        Writes error messages, these messages will be written
        regardless of the log_level (it could be set to debug,
        info, warning, error or critical).
        """
        self.logger.critical(message)

    def debug(self, message):
        """
        Writes debug messages, these messages will only be written
        if log_level is set to debug.
        """
        self.logger.debug(message)
