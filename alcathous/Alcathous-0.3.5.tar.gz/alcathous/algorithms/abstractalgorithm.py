from alcathous.nodatabehavior import NoDataBehavior
from pelops import mylogger


class AbstractAlgorithm:
    """
    AbstractAlgorithm provides everything that is needed for an algorithm to perform its aggregation work. It selects
    to correct subset of the collected data.

    config yaml:
        topic-pub-suffix: avg_5min
        algorithm: avg  # avg - average, wavg - weighted average, count, min, max
        time_window: 5  # use the values from the last ... minutes
    """

    _data_set = None  # ordered dict containing values and timestamps. It is owned the parent datapoint class instance.
    _lock_data_set = None  # prevents datapoint class to change the dataset while an algorithm process it.
    _time_window = None  # time window in seconds. e.g. use the values from the last 300s and calculate their average.
    _no_data_behavior = None  # defines how the algorithm should react if no data is available.
    _last_valid = None  # stores the last valid result of the algorithm.
    _topic = None  # publish the result to this topic
    _mqtt_client = None  # instance of pelops.mymqttclient
    name = None  # identifier for this algorithm
    _config = None  # stores the yaml-configuration for this algorithm
    _logger = None  # logger instance

    def __init__(self, name, config, parent_logger, data_set, lock_data_set, topic_pub_prefix, mqtt_client,
                 no_data_behavior):
        """
        Constructor

        :param name: Name of the instance of the algorithm
        :param config: yaml config structure
        :param parent_logger: logger instance from the parent. a child will be spawned
        :param data_set: the data the algortihm should work with
        :param lock_data_set: the algorithm works with the data set only if a lock has been acquired successfully
        :param topic_pub_prefix: prefix+name is the topic the result will be published to
        :param mqtt_client: instance of an mymqttclient
        :param no_data_behavior: defines how the algorithm should react if no data is available.
        """
        self._logger = mylogger.get_child(parent_logger, self.__class__.__name__)
        self.name = name
        self._config = config
        self._no_data_behavior = no_data_behavior
        self._data_set = data_set
        self._lock_data_set = lock_data_set

        self._logger.info("{}.{} - __init__".format(self.__class__.__name__, name))
        self._logger.debug("{}.{} - __init__ config: ".format(self.__class__.__name__, name, self._config))
        self._topic = topic_pub_prefix + self._config["topic-pub-suffix"]
        self._logger.info("{}.{} - publish to topic '{}'.".format(self.__class__.__name__, name, self._topic))

        self._mqtt_client = mqtt_client
        self._time_window = int(self._config["time_window"]) * 60
        if self._time_window <= 0:
            self._logger.error("Value for time_window must be a positive integer larger than 0. ('{}' not > 0)".
                               format(self._time_window))
            raise ValueError("Value for time_window must be a positive integer larger than 0. ('{}' not > 0)".
                             format(self._time_window))
        self._logger.info("{}.{} - time window {} s.".format(self.__class__.__name__, name, self._time_window))

    def process(self, timestamp):
        """
        Calls the specialiced method _process and publishes the result to _topic.

        :param timestamp: timestamp of the latest value to be used. valid timestamps are within timestamp and
        (timestamp - self._time_window)
        """
        time_from = timestamp - self._time_window
        time_to = timestamp
        try:
            value = self._process(time_from, time_to)
            self._last_valid = value
            self._mqtt_client.publish(self._topic, value)
        except ValueError:
            self._logger.info("{} - process/ValueError. performing no data behavior '{}'.".
                              format(self._topic, self._no_data_behavior))
            if self._no_data_behavior == NoDataBehavior.MUTE:
                pass
            elif self._no_data_behavior == NoDataBehavior.EMPTY_MESSAGE:
                self._mqtt_client.publish(self._topic, None)
            elif self._no_data_behavior == NoDataBehavior.LAST_VALID:
                self._mqtt_client.publish(self._topic, self._last_valid)
            else:
                self._logger.error("Don't know how to handle NoDataBehavior.{}.".format(self._no_data_behavior))
                raise NotImplementedError("Don't know how to handle NoDataBehavior.{}.".format(self._no_data_behavior))

    def _process(self, time_from, time_to):
        """
        This method must be implemented by each implementation of this abstract algorithm class. This is the core
        functionality - whatever condensation with the provided data should be done it must be implemented within
        this method.

        If no_data occurs (no/not enough valid values within given time window) then a ValueError exception should be raised.

        :param time_from: earliest entry from data_set
        :param time_to: latest entry from data_set
        :return: the result of the condensation
        :raises: ValueError if no_data occured.
        """
        raise NotImplementedError()

    def execution_points_estimation(self):
        """
        Each implementation of this abstract algorithm class must provide an estimation how much execution cost.

        :return: numeric value larger than 0
        """
        raise NotImplementedError()
