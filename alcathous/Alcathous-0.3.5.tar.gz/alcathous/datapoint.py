import collections
from threading import Lock
import time
from alcathous.algorithms.algorithmfactory import AlgorithmFactory
from pelops import mylogger


class DataPoint:
    """
    A DataPoint subscribes to a single topic and applies n methods/algorithms to the recorded data set.

    config yaml for the datapoint:
      - topic-sub: /test/0/raw
        topic-pub-prefix: /test/0/aggregated/
        zero_is_valid: False  # 0 is valid or rejected
        methods: wavg_5min, avg_5min

    config yaml for the methods:

    methods:
        avg_5min:
            topic-pub-suffix: avg_5min
            algorithm: avg  # avg - average, wavg - weighted average, count, min, max
            time_window: 5  # use the values from the last ... minutes

        wavg_5min:
            topic-pub-suffix: wavg_5min
            algorithm: wavg  # avg - average, wavg - weighted average, count, min, max
            time_window: 5  # use the values from the last ... minutes
    """

    methods = None  # list of instantiated methods / algorithms
    _topic_sub = None  # the values received through this topic subscription should be processed
    _topic_pub_prefix = None  # prefix for publishing the method results
    _zero_is_valid = None  # is 0 a valid value or should it be skipped
    _max_time_window = None  # each method has its own time window. this variable stores the maximum for this datapoint.
    _data_set = None  # ordered dict containing values and timestamps. It is owned the parent datapoint class instance.
    _lock_data_set = None  # prevents datapoint class to change the dataset while an algorithm process it.
    _logger = None  # logger instance
    _mqtt_client=None  # instance of pelops.mymqttclient

    def __init__(self, config_datapoint, config_methods, mqtt_client, parent_logger, no_data_behavior):
        """
        Constructor.

        :param config_datapoint: config yaml structure of this data point
        :param config_methods: config yaml structure for all methods
        :param parent_logger: logger instance from the parent. a child will be spawned
        :param mqtt_client: instance of an mymqttclient
        :param no_data_behavior: defines how the algorithm should react if no data is available.
        """

        self._logger = mylogger.get_child(parent_logger, self.__class__.__name__)
        self._logger.info("DataPoint.__init__ - initializing")
        self._logger.debug("DataPoint.__init__ - config_datapoint: {}".format(config_datapoint))
        self._logger.debug("DataPoint.__init__ - config_methods: {}".format(config_methods))
        self._mqtt_client = mqtt_client
        self._topic_sub = str(config_datapoint["topic-sub"])
        self._logger.info("DataPoint.__init__ - topic_sub: {}".format(self._topic_sub))
        self._topic_pub_prefix = str(config_datapoint["topic-pub-prefix"])
        self._logger.info("{} - publish to '{}#'".format(self._topic_sub, self._topic_pub_prefix))
        self._data_set = collections.OrderedDict()
        self._lock_data_set = Lock()
        self._max_time_window = 0
        self._zero_is_valid = bool(config_datapoint["zero_is_valid"])

        temp_methods = [x.strip() for x in config_datapoint["methods"].split(',')]
        self.methods = AlgorithmFactory.get_instances(temp_methods, config_methods, self._logger, self._data_set,
                                                      self._lock_data_set, self._topic_pub_prefix, self._mqtt_client,
                                                      no_data_behavior)
        for m in self.methods:
            if m._time_window > self._max_time_window:
                self._max_time_window = m._time_window

        self._logger.info("{} - max time window for purging data: {} s.".format(self._topic_sub, self._max_time_window))

    def _message_handler(self, value):
        """
        Message handler - to be registered to _topic_sub in mqtt_client. Stores the received value in _data_set with
        the current time stamp.

        :param value: Message content from incoming mqtt message.
        """

        if self._is_value_valid(value):
            with self._lock_data_set:
                timestamp = time.time()
                self._data_set[timestamp] = float(value)
                self._logger.info("{} - added {}@{}s".format(self._topic_sub, value, timestamp))
                self._logger.debug(self._data_set)

    def _is_value_valid(self, value):
        """
        Checks for simple rules: 'is None' and '==0' if _zero_is_valid is not set.

        :param value:
        :return: True/False
        """

        result = True
        if value is None:
            result = False
        elif value == 0 and not self._zero_is_valid:
            result = False

        if not result:
            self._logger.info("{} - value '{}' is not valid.".format(self._topic_sub, value))
        return result

    def purge_old_values(self, timestamp):
        """
        Remove all entries in _data_set that have a time stamp that is older than timestamp.

        :param timestamp: oldest time stamp to be kept.
        """

        min_time_stamp = timestamp - self._max_time_window
        self._logger.info("{} - purging values with timestamp < '{}'.".format(self._topic_sub, min_time_stamp))
        count = 0
        list_size = len(self._data_set)
        with self._lock_data_set:
            while len(self._data_set) and (next(iter(self._data_set.items())))[0] < min_time_stamp:
                self._logger.debug("{} - purge item '{}'.".format(self._topic_sub, (next(iter(self._data_set.items())))))
                count = count + 1
                self._data_set.popitem(False)
        self._logger.info("{} -  purged {}/{} items.".format(self._topic_sub, count, list_size))

    def start(self):
        """
        Start by subscribing to _topic_sub.
        """

        self._logger.info("Datapoint.start - subscribing to topic '{}'.".format(self._topic_sub))
        self._mqtt_client.subscribe(self._topic_sub, self._message_handler)

    def stop(self):
        """
        Stop by unsubscription from _topic_sub.
        """

        self._logger.info("Datapoint.stop - unsubscribing to topic '{}'.".format(self._topic_sub))
        self._mqtt_client.unsubscribe(self._topic_sub, self._message_handler)
