import unittest
import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from threading import Lock, Event
import tests_unit.testdatagenerator as testdatagenerator
from pelops import mylogger, mymqttclient, myconfigtools
from alcathous.algorithms.average import Average
from alcathous.algorithms.weightedaverage import WeightedAverage
from alcathous.algorithms.count import Count
from alcathous.algorithms.maximum import Maximum
from alcathous.algorithms.minimum import Minimum
from alcathous.nodatabehavior import NoDataBehavior


class Tools:
    def _on_response(self, value):
        self.last_response = value.decode("utf-8")
        self.on_response_sync.set()

    def _wait_for_response(self, message):
        if not self.on_response_sync.wait(1):
            self.fail("Timeout waiting on below response for message '{}'.".format(message))
        self.on_response_sync.clear()

    def _setUp(self):
        self.mqtt_client = mymqttclient.MyMQTTClient(self.config["mqtt"], self.logger, True)
        self.mqtt_client.connect()
        self.lock_data_set = Lock()
        self.end_time, self.data_set = testdatagenerator.generate_test_data(number_entries=100, time_interval=30)
        self.on_response_sync = Event()
        self.on_response_sync.clear()
        self.last_response = None
        self.pos = 0
        try:
            for m in self.config["data-preparation"]["methods"]:
                if m["name"] == self.name:
                    self.config_alg = m
            self.pub_prefix = self.config["data-preparation"]["datapoints"][self.pos]["topic-pub-prefix"]
            self.pub_suffix = self.config_alg["topic-pub-suffix"]
            self.no_data_behavior = NoDataBehavior.get_enum(self.config["data-preparation"]["no_data_behavior"])
        except KeyError:
            raise ValueError("config malformed.")

    def _tearDown(self):
        self.mqtt_client.disconnect()


class TestAlgorithmAvg(unittest.TestCase, Tools):
    @classmethod
    def setUpClass(cls):
        cls.config = myconfigtools.read_config(
            os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))+"/tests_unit/config.yaml")
        cls.logger = mylogger.create_logger(cls.config["logger"], __name__)
        cls.logger.info("TestAlgorithmAvg - start")

    @classmethod
    def tearDownClass(cls):
        cls.logger.info("TestAlgorithmAvg - stop")

    def setUp(self):
        self.name = "avg_5min"
        self._setUp()

    def tearDown(self):
        self._tearDown()

    def test_avg0_init(self):
        alg = Average(self.name, self.config_alg, self.logger, self.data_set, self.lock_data_set, self.pub_prefix,
                      self.mqtt_client, self.no_data_behavior)
        self.assertEqual(alg.name, self.name)
        self.assertEqual(alg._time_window, 300)
        self.assertEqual(len(alg._data_set), 100)
        self.assertEqual(alg._no_data_behavior, NoDataBehavior.LAST_VALID)
        self.assertEqual(alg._last_valid, None)
        self.assertEqual(alg._topic, self.pub_prefix + self.pub_suffix)
        self.assertIsNotNone(alg._mqtt_client)
        self.assertIsNotNone(alg._logger)
        self.assertEqual(alg._config, self.config_alg)

    def test_avg1_execution_points_estimation(self):
        alg = Average(self.name, self.config_alg, self.logger, self.data_set, self.lock_data_set, self.pub_prefix,
                      self.mqtt_client, self.no_data_behavior)
        self.assertEqual(alg.execution_points_estimation(), 300)

    def test_avg2_process(self):
        alg = Average(self.name, self.config_alg, self.logger, self.data_set, self.lock_data_set, self.pub_prefix,
                      self.mqtt_client, self.no_data_behavior)
        self.mqtt_client.subscribe(alg._topic, self._on_response)
        alg.process(self.end_time)
        self._wait_for_response("process average")
        self.assertIsNotNone(self.last_response)
        self.assertEqual(alg._last_valid, 5.0)
        self.assertEqual(float(self.last_response), 5.0)


class TestAlgorithmWAvg(unittest.TestCase, Tools):
    @classmethod
    def setUpClass(cls):
        cls.config = myconfigtools.read_config(
            os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))+"/tests_unit/config.yaml")
        cls.logger = mylogger.create_logger(cls.config["logger"], __name__)
        cls.logger.info("TestAlgorithmWAvg - start")

    @classmethod
    def tearDownClass(cls):
        cls.logger.info("TestAlgorithmWAvg - stop")

    def setUp(self):
        self.name = "wavg_5min"
        self._setUp()

    def tearDown(self):
        self._tearDown()

    def test_wavg0_init(self):
        alg = WeightedAverage(self.name, self.config_alg, self.logger, self.data_set, self.lock_data_set,
                              self.pub_prefix, self.mqtt_client, self.no_data_behavior)
        self.assertEqual(alg.name, self.name)
        self.assertEqual(alg._time_window, 300)
        self.assertEqual(len(alg._data_set), 100)
        self.assertEqual(alg._no_data_behavior, NoDataBehavior.LAST_VALID)
        self.assertEqual(alg._last_valid, None)
        self.assertEqual(alg._topic, self.pub_prefix + self.pub_suffix)
        self.assertIsNotNone(alg._mqtt_client)
        self.assertIsNotNone(alg._logger)
        self.assertEqual(alg._config, self.config_alg)

    def test_wavg1_execution_points_estimation(self):
        alg = WeightedAverage(self.name, self.config_alg, self.logger, self.data_set, self.lock_data_set,
                              self.pub_prefix, self.mqtt_client, self.no_data_behavior)
        self.assertEqual(alg.execution_points_estimation(), 330)

    def test_wavg2_process(self):
        alg = WeightedAverage(self.name, self.config_alg, self.logger, self.data_set, self.lock_data_set,
                              self.pub_prefix, self.mqtt_client, self.no_data_behavior)
        self.mqtt_client.subscribe(alg._topic, self._on_response)
        alg.process(self.end_time)
        self._wait_for_response("process weighted average")
        self.assertIsNotNone(self.last_response)
        self.assertEqual(alg._last_valid, 3.0)
        self.assertEqual(float(self.last_response), 3.0)


class TestAlgorithmCount(unittest.TestCase, Tools):
    @classmethod
    def setUpClass(cls):
        cls.config = myconfigtools.read_config(
            os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))+"/tests_unit/config.yaml")
        cls.logger = mylogger.create_logger(cls.config["logger"], __name__)
        cls.logger.info("TestAlgorithmCount - start")

    @classmethod
    def tearDownClass(cls):
        cls.logger.info("TestAlgorithmCount - stop")

    def setUp(self):
        self.name = "count_2min"
        self._setUp()

    def tearDown(self):
        self._tearDown()

    def test_count0_init(self):
        alg = Count(self.name, self.config_alg, self.logger, self.data_set, self.lock_data_set,
                    self.pub_prefix, self.mqtt_client, self.no_data_behavior)
        self.assertEqual(alg.name, self.name)
        self.assertEqual(alg._time_window, 120)
        self.assertEqual(len(alg._data_set), 100)
        self.assertEqual(alg._no_data_behavior, NoDataBehavior.LAST_VALID)
        self.assertEqual(alg._last_valid, None)
        self.assertEqual(alg._topic, self.pub_prefix + self.pub_suffix)
        self.assertIsNotNone(alg._mqtt_client)
        self.assertIsNotNone(alg._logger)
        self.assertEqual(alg._config, self.config_alg)

    def test_count1_execution_points_estimation(self):
        alg = Count(self.name, self.config_alg, self.logger, self.data_set, self.lock_data_set,
                    self.pub_prefix, self.mqtt_client, self.no_data_behavior)
        self.assertEqual(alg.execution_points_estimation(), 108)

    def test_count2_process(self):
        alg = Count(self.name, self.config_alg, self.logger, self.data_set, self.lock_data_set,
                    self.pub_prefix, self.mqtt_client, self.no_data_behavior)
        self.mqtt_client.subscribe(alg._topic, self._on_response)
        alg.process(self.end_time)
        self._wait_for_response("process count")
        self.assertIsNotNone(self.last_response)
        self.assertEqual(alg._last_valid, 5)
        self.assertEqual(int(self.last_response), 5)


class TestAlgorithmMin(unittest.TestCase, Tools):
    @classmethod
    def setUpClass(cls):
        cls.config = myconfigtools.read_config(
            os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))+"/tests_unit/config.yaml")
        cls.logger = mylogger.create_logger(cls.config["logger"], __name__)
        cls.logger.info("TestAlgorithmMin - start")

    @classmethod
    def tearDownClass(cls):
        cls.logger.info("TestAlgorithmMin - stop")

    def setUp(self):
        self.name = "min_3min"
        self._setUp()

    def tearDown(self):
        self._tearDown()

    def test_min0_init(self):
        alg = Minimum(self.name, self.config_alg, self.logger, self.data_set, self.lock_data_set,
                      self.pub_prefix, self.mqtt_client, self.no_data_behavior)
        self.assertEqual(alg.name, self.name)
        self.assertEqual(alg._time_window, 180)
        self.assertEqual(len(alg._data_set), 100)
        self.assertEqual(alg._no_data_behavior, NoDataBehavior.LAST_VALID)
        self.assertEqual(alg._last_valid, None)
        self.assertEqual(alg._topic, self.pub_prefix + self.pub_suffix)
        self.assertIsNotNone(alg._mqtt_client)
        self.assertIsNotNone(alg._logger)
        self.assertEqual(alg._config, self.config_alg)

    def test_min1_execution_points_estimation(self):
        alg = Minimum(self.name, self.config_alg, self.logger, self.data_set, self.lock_data_set,
                      self.pub_prefix, self.mqtt_client, self.no_data_behavior)
        self.assertEqual(alg.execution_points_estimation(), 180)

    def test_min2_process(self):
        alg = Minimum(self.name, self.config_alg, self.logger, self.data_set, self.lock_data_set,
                      self.pub_prefix, self.mqtt_client, self.no_data_behavior)
        self.mqtt_client.subscribe(alg._topic, self._on_response)
        alg.process(self.end_time)
        self._wait_for_response("process min")
        self.assertIsNotNone(self.last_response)
        self.assertEqual(alg._last_valid, 0)
        self.assertEqual(float(self.last_response), 0)


class TestAlgorithmMax(unittest.TestCase, Tools):
    @classmethod
    def setUpClass(cls):
        cls.config = myconfigtools.read_config(
            os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))+"/tests_unit/config.yaml")
        cls.logger = mylogger.create_logger(cls.config["logger"], __name__)
        cls.logger.info("TestAlgorithmMax - start")

    @classmethod
    def tearDownClass(cls):
        cls.logger.info("TestAlgorithmMax - stop")

    def setUp(self):
        self.name = "max_3min"
        self._setUp()

    def tearDown(self):
        self._tearDown()

    def test_max0_init(self):
        alg = Maximum(self.name, self.config_alg, self.logger, self.data_set, self.lock_data_set,
                      self.pub_prefix, self.mqtt_client, self.no_data_behavior)
        self.assertEqual(alg.name, self.name)
        self.assertEqual(alg._time_window, 180)
        self.assertEqual(len(alg._data_set), 100)
        self.assertEqual(alg._no_data_behavior, NoDataBehavior.LAST_VALID)
        self.assertEqual(alg._last_valid, None)
        self.assertEqual(alg._topic, self.pub_prefix + self.pub_suffix)
        self.assertIsNotNone(alg._mqtt_client)
        self.assertIsNotNone(alg._logger)
        self.assertEqual(alg._config, self.config_alg)

    def test_max1_execution_points_estimation(self):
        alg = Maximum(self.name, self.config_alg, self.logger, self.data_set, self.lock_data_set,
                      self.pub_prefix, self.mqtt_client, self.no_data_behavior)
        self.assertEqual(alg.execution_points_estimation(), 180)

    def test_max2_process(self):
        alg = Maximum(self.name, self.config_alg, self.logger, self.data_set, self.lock_data_set,
                      self.pub_prefix, self.mqtt_client, self.no_data_behavior)
        self.mqtt_client.subscribe(alg._topic, self._on_response)
        alg.process(self.end_time)
        self._wait_for_response("process max")
        self.assertIsNotNone(self.last_response)
        self.assertEqual(alg._last_valid, 6)
        self.assertEqual(float(self.last_response), 6)


if __name__ == '__main__':
    unittest.main()
