"""
A module that contains definition of TimeSeriesLogger class that is used by AML forecasting package for logging purpose.
"""
import sys
from time import time
from datetime import timedelta

from azureml.train._telemetry_logger import _TelemetryLogger
from logging import Logger, INFO, DEBUG, StreamHandler
from ftk.constants import LOGGING_PREFIX, LOGGING_DATETIME_FORMAT

class TimeSeriesLogger(Logger):
    """
    Logging class for the forecasting toolkit.
    """
    def __init__(self, prefix=LOGGING_PREFIX):
        """
        :param prefix: The logging prefix.
        :param datetime_format: The datetime format to be used in logging when needed.
        """

        super(TimeSeriesLogger, self).__init__(LOGGING_PREFIX)
        self.handlers = []
        lhPermissiveHandler=StreamHandler(sys.stdout)
        lhPermissiveHandler.setLevel(DEBUG)
        self.addHandler(lhPermissiveHandler)
        self._logging_prefix = prefix
    

    def _construct_final_message(self, message):
        message = '{0} - {1}'.format(self._logging_prefix, message)
        return message
    

    def log_start(self, activity_name, program, custom_dimensions=None):
        """
        Log the start of the program and return the start time.
        :param program: string. The name of the program to be logged.
        :return: float. Program start time expressed in seconds since the epoch.
        """

        message = '{0} started.'.format(program)
        message = self._construct_final_message(message)
        start_time = time()
        self.log_info(activity_name, message, custom_dimensions)
        self.log(INFO, message+' %s', '')
        return start_time


    def log_end(self, activity_name, program, start_time, custom_dimensions=None):
        """
        Log the end of the program and print out the elpased time.
        :param program: string. The name of the program to be logged.
        :param start_time: float. Program start time expressed in seconds since the epoch.
        :return: None
        """

        end_time = time()
        elapsed = str(timedelta(seconds=end_time - start_time))
        message = '{0} finished. Time elapsed'.format(program)
        message = self._construct_final_message(message)
        self.log_info(activity_name, message, custom_dimensions)
        self.log(INFO, message+' %s', str(elapsed))
        
    def log_info(self, activity_name, message, custom_dimensions):
        """
        Log the telemetry information and message with the with Info level.
        
        :param activity_name: the name of the activity which should be unique per the wrapped logical code block
        :type activity_name: str
        :param message: The message to be logged.
        :type message: str
        :param custom_dimensions: custom properties of the activity
        :type custom_dimensions: dict
        
        """
        logger = _TelemetryLogger.get_telemetry_logger(__name__)
        with _TelemetryLogger.log_activity(logger,
                                           activity_name,
                                           custom_dimensions=custom_dimensions) as activity_logger:
            activity_logger.info(message)
    
    def setLevel(self, log_level):
        """
        Temporary do nothing.
        """
        pass
