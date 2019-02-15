from pelops.abstractmicroservice import AbstractMicroservice
import time
import threading
from alcathous.datapoint import DataPoint
from alcathous.nodatabehavior import NoDataBehavior
from alcathous.worker import Worker
import alcathous.schema as schema
from alcathous import version


class DataPointManager(AbstractMicroservice):
    """
    Manage the data points by creating/start/stopping them and invocation of the process methods of the algorithms
    regularly.

    Config yaml:
    mqtt:
        mqtt-address: localhost
        mqtt-port: 1883
        credentials-file: ~/credentials.yaml
        log-level: INFO

    logger:
        log-level: DEBUG
        log-file: alcathous.log

    data-preparation:  # alcathous root node
        no_data_behavior: last_valid  # mute, last_valid, empty_message
        update_cycle: 30  # new values published each ... seconds
        number_worker: 2  # how many worker threads should be spawned to process task queue

        methods:
            avg_5min:
                topic-pub-suffix: avg_5min
                algorithm: avg  # avg - average, wavg - weighted average, count, min, max
                time_window: 5  # use the values from the last ... minutes

            wavg_5min:
                topic-pub-suffix: wavg_5min
                algorithm: wavg  # avg - average, wavg - weighted average, count, min, max
                time_window: 5  # use the values from the last ... minutes

        datapoints:
            - topic-sub: /test/0/raw
              topic-pub-prefix: /test/0/aggregated/
              zero_is_valid: False  # 0 is valid or rejected
              methods: wavg_5min, avg_5min
    """
    _version = version

    _data_points = None  # list of datapoint instances
    _processes = None  # list with references to all process functions of the algorithms of the datapoints
    _purges = None  # list with references to all purge functions of the datapoints
    _no_data_behavior = None  # defines how the algorithm should react if no data is available.
    _update_cycle = None  # call all processes every n seconds
    _worker = None  # instance of the worker manager
    _do_loop_thread = None  # contains the loop method thread

    def __init__(self, config, mqtt_client=None, logger=None):
        """
        Constructor.

        :param config: config yaml structure
        :param mqtt_client: instance of an mymqttclient (optional)
        :param logger: instance of a logger (optional)
        """

        AbstractMicroservice.__init__(self, config, "data-preparation", mqtt_client=mqtt_client, logger=logger)

        self._purges = []
        self._processes = []
        self._data_points = []

        self._update_cycle = int(self._config["update_cycle"])
        self._no_data_behavior = NoDataBehavior.get_enum(str(self._config["no_data_behavior"]))

        self._worker = Worker(self._config["number_worker"], self._logger)
        self._do_loop_thread = threading.Thread(target=self._do_loop)

        _config_methods = {}
        for m in self._config["methods"]:
            key = m["name"]
            if key in _config_methods:
                self._logger.error("DataPointManager - method name must be unique ({}).".format(key))
                raise ValueError("DataPointManager - method name must be unique ({}).".format(key))
            _config_methods[key] = m

        for config_data_point in self._config["datapoints"]:
            dp = DataPoint(config_data_point, _config_methods, self._mqtt_client, self._logger,
                           self._no_data_behavior)
            self._purges.append(dp.purge_old_values)
            for method in dp.methods:
                process = method.process
                cost = method.execution_points_estimation()
                self._logger.info("DataPointManager - adding process '{}' with cost '{}'.".
                                  format(process.__name__, cost))
                self._processes.append((process, cost))
            self._data_points.append(dp)

        self._processes.sort(key=lambda tup: tup[1], reverse=True)  # sort processes by their cost most expensive first

    @classmethod
    def _get_description(cls):
        return "This software subscribes to mqtt-topics that contain raw sensor data and publishes average values " \
               "for configurable time spans."

    def _loop_process(self):
        """
        Call all process and purge methods.
        """

        timestamp = time.time()
        self._logger.info("DataPointManager - started work for timestamp '{} s'.".format(timestamp))
        for p in self._processes:
            self._worker.queue.put((p[0], timestamp))
            self._logger.info("DataPointManager - waiting for worker to finish processing the algorithms.")
        self._worker.queue.join()
        for p in self._purges:
            self._worker.queue.put((p, timestamp))
        self._logger.info("DataPointManager - waiting for worker to purge outdated values.")
        self._worker.queue.join()

    def _do_loop(self):
        """
        Call _loop_process every n seconds.
        """
        self._logger.info("DataPointManager - start loop.")
        while not self._stop_service.is_set():
            start = time.time()
            self._loop_process()
            sleep_for = max(0, self._update_cycle - (time.time() - start))
            self._logger.info("DataPointManager - wait for '{} s'.".format(sleep_for))
            self._stop_service.wait(sleep_for)
        self._logger.info("DataPointManager - exited loop.")

    @classmethod
    def _get_schema(cls):
        """
        Get the sub schema to validate the yaml-config file against.

        :return: json-schema dict
        """
        return schema.get_schema()

    def _start(self):
        """
        Start all datapoints, worker and the process loop.
        """
        for dp in self._data_points:
            dp.start()
        self._worker.start()
        self._do_loop_thread.start()

    def _stop(self):
        """
        Stop all datapoints, worker and the process loop.
        """
        for dp in self._data_points:
            dp.stop()
        self._do_loop_thread.join()
        self._worker.stop()


def standalone():
    """Calls the static method DataPointManager.standalone()."""
    DataPointManager.standalone()


if __name__ == "__main__":
    DataPointManager.standalone()
