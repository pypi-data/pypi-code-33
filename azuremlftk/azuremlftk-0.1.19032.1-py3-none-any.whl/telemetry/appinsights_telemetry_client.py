###
#
# This is the telemetry API.
#
# These calls are intended to be used in toolkit code, not by user.
#
import logging;

from ftk.telemetry import AbstractTelemetryClient, TelemetryImplementationBase, TelemetryConst, LogconfigFactory
from azureml.telemetry.logging_handler import AppInsightsLoggingHandler
##############################################################################
    
class AppInsightsTelemetryClient(AbstractTelemetryClient):
    """
    Telemetry client for use by toolkits. 
    This implementation of Telemetry client uses ApplicationInsights as a Backend.
    Current implementation uses the logging pathway.

    In toolkit code, we do this:

    >>> class FTKAMLLogTelemetryClient(AMLLogTelemetryClient):
    >>>     def __init__(self):
    >>>         super(FTKAMLLogTelemetryClient, TelemetryConst.FTK_TELEMETRY_PREFIX)

    >>> from ftk_telemetry_client import FTKAMLLogTelemetryClient;
    >>> teleclient = FTKAMLLogTelemetryClient();
    >>> teleclient.emit(TelemetryConst.MSG_PKG_INIT, teleclient.user_deid())

    >>> teleclient.emit_deployment_start()
    >>> try:
    >>>     pipeline.deploy();
    >>>     teleclient.emit_deployment_end();
    >>> except Toolkit as e:
    >>>     teleclient.emit_deployment_fail();

    :param prefix: The prefix to be used with the logger.
    :type prefix: str
    :param instrumentation_key: the instrumentation key used by the logger.
    :type instrumentation_key: str
    :param log_machine_info: if True the machine info will be emitted.
    :type log_machine_info: bool
    
    """
    DEFAULT_LOG_LEVEL = logging.INFO
    ini_file_name = "Telemetry.ini"
    
    
    def __init__(self,  prefix, instrumentation_key, log_machine_info=False):
        """Constructor.
        
        :param prefix: The prefix to be used with the logger.
        :type prefix: str
        :param instrumentation_key: the instrumentation key used by the logger.
        :type instrumentation_key: str
        :param log_machine_info: if True the machine info will be emitted.
        :type log_machine_info: bool
        
        """
        self._instrumentation_key=instrumentation_key
        self._level = AppInsightsTelemetryClient.DEFAULT_LOG_LEVEL
        super(AppInsightsTelemetryClient, self).__init__(prefix, log_machine_info)
    
    def _get_impl(self):
        """
        Return the telemetry client implementation.
        
        :returns: telemetry client implementation.
        :rtype: AppInsightsTelemetryClientImpl
        """
        return self._telemetry_client
    
    def _retrieve_or_create_self(self, prefix, log_machine_info):
        """
        Retrieve the instance of self from AbstractTelemetryClient._instances, if it is not there
        create a new instance and add it to AbstractTelemetryClient._instances.
        
        :param prefix: The prefix to be used with the logger.
        :type prefix: str
        :param log_machine_info: if True the machine info will be emitted.
        :type log_machine_info: bool
        
        """
        if type(self) in AbstractTelemetryClient._instances.keys():
            self._telemetry_client = AbstractTelemetryClient._instances[type(self)]._telemetry_client
            AbstractTelemetryClient.setup(self, prefix=prefix, log_machine_info=log_machine_info)
        else:
            self._telemetry_client = AppInsightsTelemetryClientImpl(prefix=prefix, log_machine_info=log_machine_info, instrumentation_key=self._instrumentation_key)
            AbstractTelemetryClient._instances[type(self)] = self

class AppInsightsTelemetryClientImpl(TelemetryImplementationBase):
    """
    The private class doing actual job.
    
    """
    
    # telemetry client emits values
    def emit(self, key, value, logging_level=logging.INFO):
        """
        Emit the message to the Appinsights.
        
        :param key: The tey value
        :type key: str
        :param value: metrics value.
        :type value: str
        :param logging_level: the logging level as in logging package.
        :type logging_level: int
         
        """
        self.get_logger().log(logging_level, self._prefix + ':' + str(key) + ' ' + str(value))
        
    def getLevel(self):
        """
        Convenience method to return current log level of logger, belonging to AppInsightsTelemetryClient.
        
        :returns: current logging level.
        :rtype: int
        """
        return self.getHandlerMinLogLevel()
    
    def setHandlerLogLevel(self, log_level):
        """
        Convenience method to set the logging level for all log handlers of the local logger
        belonging to AMLLogTelemetryClient.
        
        :param log_level: The log level to be set to handlers.
        :type log_level: int
        
        """
        self._logger.setLevel(log_level)
        for handler in self._logger.handlers:
            handler.setLevel(log_level)
            
    def getHandlerMinLogLevel(self):
        """
        Convenience method to return the minimal level for handlers of the local logger
        belonging to AMLLogTelemetryClient.
        
        :returns: level.
        :rtype: int
        """
        min_level = logging.NOTSET
        if len(self._logger.handlers)>0:
            min_level = self._logger.handlers[0].level
            for handler in self._logger.handlers[1:]:
                min_level = min(handler.level, min_level)
        return min_level
    
    def get_logger(self):
        """
        Return the logger used by the TelemetryClient.
        
        :return: The logger compatible with logging.logger.
        :rtype: logging.logger
        """
        return self._logger
    
    def retrieve_or_create_logger(self, **kwargs):
        """
        Create the logger which will beb returned by get_logger()
        
        :param instrumentation_key: the instrumentation key used by the logger.
        :type instrumentation_key: str
        
        """
        instrumentation_key = kwargs.get('instrumentation_key')
        self._logger = logging.getLogger(TelemetryConst.TELEMETRY_CLIENT_NAME)
        #Try to read local logger configuration from the file.
        #If file is not present create it.
        if LogconfigFactory(AppInsightsTelemetryClient.ini_file_name, 
                            TelemetryConst.TELEMETRY_CLIENT_NAME, 
                            log_level=AppInsightsTelemetryClient.DEFAULT_LOG_LEVEL).getSuccess():
            logging.config.fileConfig(AppInsightsTelemetryClient.ini_file_name, disable_existing_loggers=False)
            self._logger = logging.getLogger(TelemetryConst.TELEMETRY_CLIENT_NAME)
        else:
            #If file reading and creation failed, set the default parameters.
            self._logger = logging.getLogger(TelemetryConst.TELEMETRY_CLIENT_NAME)
            if not self._logger.hasHandlers():
                lhPermissiveHandler=logging.StreamHandler()
                lhPermissiveHandler.setLevel(AppInsightsTelemetryClient.DEFAULT_LOG_LEVEL)
                self._logger.addHandler(lhPermissiveHandler)
        has_handler = False
        for handler in self._logger.handlers:
            if isinstance(handler, AppInsightsLoggingHandler):
                has_handler=True
                break
        if not has_handler:
            azureml_handler = AppInsightsLoggingHandler(instrumentation_key, self._logger)
            self._logger.addHandler(azureml_handler)
        self.setHandlerLogLevel(self._logger.level)
        