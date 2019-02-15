from pelops import mylogger
from pelops import myconfigtools
from pelops.mymqttclient import MyMQTTClient
import argparse
import json
import threading
import pelops.schema.abstractmicroservice


class AbstractMicroservice:
    """
    Base class for all MicroServices of pelops. Takes care of reading and validating the config, providing mymqttclient
    and logger instances as well as static methods to create an instance and run it indefinitly.

    If no mqtt client has been provided, the config must have an "mqtt" entry at root level. Same accounts for the
    logger.

    An implementation of this abstract class should use the provided config, mqtt_client, and logger. But most
    importantly, it must adhere to the _is_stopped and _stop_service Events and make good use of the _start and
    _stop methods. Otherwise, starting and stopping the microservice might not be possible in the framework.

    The two events/flags _is_started and _is_stopped show the state of the Service. They are changed in the methods
    start and stop. During the start and the stopped sequences, both events are cleared. Thus, in case of an error
    during these sequences, the state of the microservice is undefined.
    """

    _config = None  # config yaml structure
    _is_stopped = None  # event that is True if the service is not running
    _is_started = None  # event that is True if the service is running
    _stop_service = None  # event that must be used by all internal loops. if evet fires, they must stop.
    _startstop_lock = None  # lock start/stop routine - prevents from interrupting an ongoing start/stop process
    _asyncstart_thread = None  # thread for asnychronous start
    _asyncstop_thread = None  # thread for asynchronous stop
    _mqtt_client = None  # mymqttclient instance
    _logger = None  # logger instance
    _stop_mqtt_client = None  # if mqtt_client has been created by this instance, it should be shutdown as well

    def __init__(self, config, config_class_root_node_name, mqtt_client=None, logger=None, logger_name=None):
        """
        Constructor

        :param config: config yaml structure
        :param config_class_root_node_name: string - name of root node of microservice config
        :param mqtt_client: mymqttclient instance
        :param logger: logger instance - optional
        :param logger_name: name for logger instance - optional
        """
        self._config = config[config_class_root_node_name]

        if logger_name is None:
            logger_name = __name__

        if logger is None:
            self._logger = mylogger.create_logger(config["logger"], logger_name)
        else:
            self._logger = logger.getChild(logger_name)

        self._logger.info("{}.__init__ - initializing".format(self.__class__.__name__))
        self._logger.debug("{}.__init__ - config: {}".format(self.__class__.__name__, self._config))

        self._is_stopped = threading.Event()
        self._is_stopped.set()
        self._is_started = threading.Event()
        self._is_started.clear()

        self._stop_service = threading.Event()
        self._stop_service.clear()

        if mqtt_client is None:
            self._mqtt_client = MyMQTTClient(config["mqtt"], self._logger)
            self._stop_mqtt_client = True
        else:
            self._mqtt_client = mqtt_client
            self._stop_mqtt_client = False

        self._startstop_lock = threading.Lock()
        self._asyncstart_thread = threading.Thread(target=self.start)
        self._asyncstop_thread = threading.Thread(target=self.stop)

        self._logger.info("{}.__init__ - AbstractMicroservice done".format(self.__class__.__name__))

    def _start(self):
        """abstract start method - to be implemented by child"""
        self._logger.warning("{}._start - NotImplementedError".format(self.__class__.__name__))
        raise NotImplementedError

    def asyncstart(self):
        """start microservice and return immediately (dont wait until start has been finished)"""
        self._logger.info("{} - async start".format(self.__class__.__name__))
        self._asyncstart_thread.start()

    def asyncstop(self):
        """stop microservice and return immediately (dont wait until stop has been finished)"""
        self._logger.info("{} - async stop".format(self.__class__.__name__))
        self._asyncstop_thread.start()

    def start(self):
        """start microservice - resets events, starts mymqttclient, and calls _start."""
        print("{} - starting".format(self.__class__.__name__))
        self._logger.info("{} - starting".format(self.__class__.__name__))
        with self._startstop_lock:
            self._logger.info("{} - start_lock acquired".format(self.__class__.__name__))
            self._is_stopped.clear()
            self._stop_service.clear()
            if not self._mqtt_client.is_connected.is_set():
                self._mqtt_client.connect()
                self._mqtt_client.is_connected.wait()
            else:
                self._logger.info("{} - mqtt_client is already running".format(self.__class__.__name__))
            self._start()
            self._is_started.set()
            self._logger.info("{} - started".format(self.__class__.__name__))

    def _stop(self):
        """abstract stop method - to be implemented by child"""
        self._logger.warning("{}._stop - NotImplementedError".format(self.__class__.__name__))
        raise NotImplementedError

    def stop(self):
        """stop microservice - sets _stop_service event, calls _stop and sets _is_stopped."""
        self._logger.info("{} - stopping".format(self.__class__.__name__))
        with self._startstop_lock:
            self._logger.info("{} - _stop_lock acquired".format(self.__class__.__name__))
            self._is_started.clear()
            self._stop_service.set()
            self._stop()
            if self._stop_mqtt_client:
                self._mqtt_client.disconnect()
                self._mqtt_client.is_disconnected.wait()
            print("{} - stopped".format(self.__class__.__name__))
            self._is_stopped.set()
            self._logger.info("{} - stopped".format(self.__class__.__name__))

    def runtimeinformation(self):
        """return runtime information in a dict for logging/monitoring purposes."""
        return {}

    @classmethod
    def _get_schema(cls):
        """
        Returns the child specific json schema - to be implemented by child.

        :return: json schema struct
        """
        raise NotImplementedError

    @classmethod
    def get_schema(cls):
        return pelops.schema.abstractmicroservice.get_schema(cls._get_schema())

    @classmethod
    def dump_schema(cls, filename):
        """
        Dumps the latest schema to the provided file but only iff the contents differ. If no file is found, a new file
        will be generated.

        :param filename - path to autogenerated config schema json file
        """
        new_schema = json.dumps(cls.get_schema(), indent=4)

        try:
            with open(filename, 'r') as f:
                old_schema = f.read()
        except OSError:
            old_schema = ""

        if new_schema != old_schema:
            print("updating {} to latest schema.".format(filename))
            with open(filename, 'w') as f:
               f.write(new_schema)


    @classmethod
    def _get_description(cls):
        """
        Shortescription of microservice. Used for command line interface output.

        :return: string
        """
        raise NotImplementedError

    @classmethod
    def _args_to_config(cls, args=None):
        """Handle command line arguments and read the yaml file into a json structure (=config)."""
        desc = cls._get_description()
        ap = argparse.ArgumentParser(description=desc)
        ap.add_argument('-c', '--config', type=str, help='yaml config file', required=True)
        ap.add_argument('--version', action='version',
                            version='%(prog)s {}'.format(cls._version),
                            help='show the version number and exit')
        if args:
            arguments = vars(ap.parse_args(args))
        else:
            arguments = vars(ap.parse_args())

        config_filename = arguments["config"]
        config = myconfigtools.read_config(config_filename)

        return config

    def run(self):
        """
        execution loop - starts, waits infinitely for keyboardinterupt, and stops if this interrupt happend.
        """
        self.start()

        try:
            while not self._is_stopped.wait(0.25):  # timeout is necessary for CTRL+C
                pass
        except KeyboardInterrupt:
            self._logger.info("KeyboardInterrupt")
            self.stop()

    @classmethod
    def standalone(cls, args=None):
        """Public method to start this driver directly. Instantiates an mymqttclient and creates an object for the
                given driver."""
        config = cls._args_to_config(args)
        config = myconfigtools.dict_deepcopy_lowercase(config)

        schema = cls.get_schema()
        validation_result = myconfigtools.validate_config(config, schema)
        if validation_result:
            raise ValueError("Validation of config file failed: {}".format(validation_result))

        instance = None

        try:
            instance = cls(config)
            instance.run()
        except Exception as e:
            if instance is not None and instance._logger is not None:
                instance._logger.exception(e)
            raise

