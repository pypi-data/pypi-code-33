import socket
import getpass
import numpy as np

from abc import ABCMeta, abstractmethod

from ftk.telemetry import AbstractTelemetryClient, TelemetryConst
import logging

class TelemetryImplementationBase(metaclass=ABCMeta):
    """
    The private class doing actual job.
    
    """
    def __init__(self, prefix, log_machine_info=False, **kwargs):
        self._prefix = prefix
        self._last_depid = None
        self._last_expid = None
        self.retrieve_or_create_logger(**kwargs)
        if log_machine_info:
            AbstractTelemetryClient.log_machine_info(self)
    
    def format_maybe(self, message, classname):
        return ' '.join([classname, message]).strip()
        
    def get_prefix(self):
        """
        Return the prefix of the telemetry client.
        
        :returns: the prefix of the telemetry client.
        :rtype: str
        
        """    
        return self._prefix

    # standard methods for generating IDs
    def user_deid(self):
        return hash(socket.gethostname() + ' ' + getpass.getuser())

    # record standard events
    def emit_deployment_start(self):
        #2147483647 is the largest value for int32
        self._last_depid = np.random.randint(2147483647)
        self.emit(TelemetryConst.MSG_DEPLOY_START, self._last_depid, logging.INFO)

    def emit_deployment_end(self):        
        self.emit(TelemetryConst.MSG_DEPLOY_END, self._last_depid, logging.INFO)

    def emit_deployment_fail(self):
        self.emit(TelemetryConst.MSG_DEPLOY_FAIL, self._last_depid, logging.ERROR)

    def emit_deployment_delete(self):
        self.emit(TelemetryConst.MSG_DEPLOY_FAIL, self._last_depid, logging.WARNING)

    def emit_experiment_start(self, classname=''):
        #2147483647 is the largest value for int32
        self._last_expid = np.random.randint(2147483647)
        self.emit(self.format_maybe(TelemetryConst.MSG_EXPERIMENT_FIT_START, classname), self._last_expid, logging.INFO)

    def emit_experiment_end(self, classname=''):
        self.emit(self.format_maybe(TelemetryConst.MSG_EXPERIMENT_FIT_END, classname), self._last_expid, logging.INFO)

    def emit_experiment_fail(self, classname=''):
        self.emit(self.format_maybe(TelemetryConst.MSG_EXPERIMENT_FIT_FAIL, classname), self._last_expid, logging.ERROR)

    def emit_dataset_size(self, size):
        self.emit(TelemetryConst.MSG_DATASET_SIZE, size, logging.INFO)
        
    def emit_predict_end(self, classname=''):
        self.emit(self.format_maybe(TelemetryConst.MSG_EXPERIMENT_PREDICT_END, classname), self._last_expid, logging.INFO)

    def emit_predict_fail(self, classname=''):
        self.emit(self.format_maybe(TelemetryConst.MSG_EXPERIMENT_PREDICT_FAIL, classname), self._last_expid, logging.ERROR)

    def emit_predict_start(self, classname=''):
        self._last_expid = np.random.randint(2147483647)
        self.emit(self.format_maybe(TelemetryConst.MSG_EXPERIMENT_PREDICT_START, classname), self._last_expid, logging.INFO)

    def setLevel(self, level):
        """
        Convenience method to set the level.
        Avoid setting the logger level in the class methods, because it cause consequent changes in the logging level in all other program modules.
        
        :param level: - the logging level one of CRITICAL, ERROR, WARNING, INFO, DEBUG, NOTSET.
        :type level: int
        
        """
        self.setHandlerLogLevel(level)
    
    # telemetry client emits values
    @abstractmethod
    def emit(self, key, value, logging_level):
        raise NotImplementedError
    
    @abstractmethod
    def getLevel(self):
        """
        Convenience method to return current log level of logger, belonging to AMLLogTelemetryClient.
        
        :returns: current logging level.
        :rtype: int
        
        """
        raise NotImplementedError
    
    @abstractmethod
    def setHandlerLogLevel(self, log_level):
        """
        Convenience method to set the logging level for all log handlers of the local logger
        belonging to AMLLogTelemetryClient.
        
        :param log_level: The log level to be set to handlers.
        :type log_level: int
        
        """
        raise NotImplementedError
    
    @abstractmethod     
    def getHandlerMinLogLevel(self):
        """
        Convenience method to return the minimal level for handlers of the local logger
        belonging to AMLLogTelemetryClient.
        
        :returns: level.
        :rtype: int
        
        """
        raise NotImplementedError
    
    @abstractmethod
    def get_logger(self):
        """
        Return the logger used by the TelemetryClient.
        
        :return: ToolkitLogger
        
        """
        raise NotImplementedError
    
    @abstractmethod
    def retrieve_or_create_logger(self, **kwargs):
        """
        Create the logger which will be returned by get_logger()
        
        """
        raise NotImplementedError