import requests
import json
import traceback

from abc import ABCMeta, abstractmethod
from ftk.telemetry import TelemetryConst


def get_machine_info():
    """
      Get the machine information from Azure Instance Metadata service.
      
      :returns: the dctionary with machine info.
      :rtype: dict
      :raises: RequestException
      
    """
    info = {'is_dsvm': False}
    try:
        r = requests.get('http://169.254.169.254/metadata/instance?api-version=2017-08-01',
                         headers={'Metadata': 'true'},
                         timeout=1)
        json_response = r.json()
        if (json_response['compute']['publisher'] == 'microsoft-ads'
            and 'data-science-vm' in json_response['compute']['offer']):
            info = {
                'is_dsvm': True,
                'os_type': json_response['compute']['osType']
            }
    except requests.exceptions.RequestException:
        # something went wrong with the request.  most likely we're not on a dsvm and the
        # endpoint isn't available
        pass

    return info

class AbstractTelemetryClient(metaclass=ABCMeta):
    """
    The abstract class defining methods to provide telemetry.
    
    :param prefix: The prefix to be used with the logger.
    :type prefix: str
    :param log_machine_info: 
    :type log_machine_info: bool
    
    """
    _instances = {}
    
    @classmethod
    def getInstance(cls, **kwargs):
        """
        The static method to get the instance of a AMLLogTelemetryClient.
        
        """
        if cls not in AbstractTelemetryClient._instances.keys():
            AbstractTelemetryClient._instances[cls]=cls(**kwargs)
        else:
            AbstractTelemetryClient.setup(AbstractTelemetryClient._instances[cls], **kwargs)
        return AbstractTelemetryClient._instances[cls]
    
    @staticmethod
    def log_machine_info(instance):
        """
        Emit the machine info with this instance of AbstractTelemetryClient.
        
        :param instance: The instance of Telemetry client to be used to emit the message.
        :type instance: AbstractTelemetryClient
        
        """
        try:
            machine_info = get_machine_info()
            instance.emit('machine info', json.dumps(machine_info))
        except Exception as e:
            # something else went wrong.  most likely the API changed, so let's log it
            instance.logger.log('exception getting machine info:', traceback.format_exc())
    
    @staticmethod
    def setup(instance, **kwargs):
        if TelemetryConst.PREFIX in kwargs:
            instance._telemetry_client._prefix = kwargs[TelemetryConst.PREFIX]
        if kwargs.get(TelemetryConst.LOG_MACHINE_INFO, False):
            AbstractTelemetryClient.log_machine_info(instance._telemetry_client)
    
    def __init__(self, prefix, log_machine_info=False):
        """Constructor
        
        :param prefix: The prefix to be used with the logger.
        :type prefix: str
        :param log_machine_info: 
        :type log_machine_info: bool
        
        """
        self._retrieve_or_create_self(prefix, log_machine_info)
        
    def format_maybe(self, message, classname):
        return self._get_impl().format_maybe(message, classname)
        
    def get_prefix(self):
        """
        Return the prefix of the telemetry client.
        
        :returns: the prefix of the telemetry client.
        :rtype: str
        
        """    
        return self._get_impl().get_prefix()
    
    # telemetry client emits values
    def emit(self, key, value):
        self._get_impl().emit(key, value)

    # standard methods for generating IDs
    def user_deid(self):
        return self._get_impl().user_deid()

    # record standard events
    def emit_deployment_start(self):
        #2147483647 is the largest value for int32
        self._get_impl().emit_deployment_start()

    def emit_deployment_end(self):   
        self._get_impl().emit_deployment_end()     

    def emit_deployment_fail(self):
        self._get_impl().emit_deployment_fail()

    def emit_deployment_delete(self):
        self._get_impl().emit_deployment_delete()

    def emit_experiment_start(self, classname=''):
        #2147483647 is the largest value for int32
        self._get_impl().emit_experiment_start(classname=classname)

    def emit_experiment_end(self, classname=''):
        self._get_impl().emit_experiment_end(classname=classname)

    def emit_experiment_fail(self, classname=''):
        self._get_impl().emit_deployment_fail()

    def emit_dataset_size(self, size):
        self._get_impl().emit_dataset_size(size=size)
        
    def emit_predict_end(self, classname=''):
        self._get_impl().emit_predict_end(classname)

    def emit_predict_fail(self, classname=''):
        self._get_impl().emit_predict_fail(classname)

    def emit_predict_start(self, classname=''):
        self._get_impl().emit_predict_start(classname)

    def setLevel(self, level):
        """
        Convenience method to set the level on the logger used by AMLLogTelemetryClient.
        Avoid setting the logger level in the class methods, because it cause consequent changes in the logging level in all other program modules.
        
        :param level: - the logging level one of CRITICAL, ERROR, WARNING, INFO, DEBUG, NOTSET.
        :type level: int
        
        """
        self._get_impl().setLevel(level)
        
    def getLevel(self):
        """
        Convenience method to return current log level of logger, belonging to AMLLogTelemetryClient.
        
        :returns: current logging level.
        :rtype: int
        
        """
        return self._get_impl().getLevel()
    
    def setHandlerLogLevel(self, log_level):
        """
        Convenience method to set the logging level for all log handlers of the local logger
        belonging to AMLLogTelemetryClient.
        
        :param log_level: The log level to be set to handlers.
        :type log_level: int
        
        """
        self._get_impl().setHandlerLogLevel(log_level)
            
    def getHandlerMinLogLevel(self):
        """
        Convenience method to return the minimal level for handlers of the local logger
        belonging to AMLLogTelemetryClient.
        
        :returns: level.
        :rtype: int
        
        """
        return self._get_impl().getHandlerMinLogLevel()
    
    @abstractmethod
    def _get_impl(self):
        """
        Return the telemetry client implementation.
        The return type is defined by the exact implementation of TelemetryClient.
        
        :returns: telemetry client implementation.
        
        """
        raise NotImplementedError
    
    @abstractmethod
    def _retrieve_or_create_self(self, prefix, log_machine_info):
        """
        Retrieve the instance of self from AbstractTelemetryClient._instances, if it is not there
        create a new instance and add it to AbstractTelemetryClient._instances.
        
        :param prefix: The prefix to be used with the logger.
        :type prefix: str
        :param log_machine_info: 
        :type log_machine_info: bool
        
        """
        raise NotImplementedError