import unittest
import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from threading import Event
import time
import tests_unit.testdatagenerator as testdatagenerator
from pelops import mylogger, mymqttclient, myconfigtools
from alcathous.datapoint import DataPoint
from alcathous.algorithms.average import Average
from alcathous.algorithms.weightedaverage import WeightedAverage
from alcathous.algorithms.count import Count
from alcathous.algorithms.maximum import Maximum
from alcathous.algorithms.minimum import Minimum
from alcathous.nodatabehavior import NoDataBehavior


class TestDatapoint(unittest.TestCase):
    def _on_response_avg(self, value):
        self.last_response_avg = value.decode("utf-8")
        self.on_response_avg_sync.set()

    def _wait_for_response_avg(self, message):
        if not self.on_response_avg_sync.wait(1):
            self.fail("Timeout waiting on response_avg for message '{}'.".format(message))
        self.on_response_avg_sync.clear()

    def _on_response_wavg(self, value):
        self.last_response_wavg = value.decode("utf-8")
        self.on_response_wavg_sync.set()

    def _wait_for_response_wavg(self, message):
        if not self.on_response_wavg_sync.wait(1):
            self.fail("Timeout waiting on response_wavg for message '{}'.".format(message))
        self.on_response_wavg_sync.clear()

    def _on_response_count(self, value):
        self.last_response_count = value.decode("utf-8")
        self.on_response_count_sync.set()

    def _wait_for_response_count(self, message):
        if not self.on_response_count_sync.wait(1):
            self.fail("Timeout waiting on response_count for message '{}'.".format(message))
        self.on_response_count_sync.clear()

    def _on_response_min(self, value):
        self.last_response_min = value.decode("utf-8")
        self.on_response_min_sync.set()

    def _wait_for_response_min(self, message):
        if not self.on_response_min_sync.wait(1):
            self.fail("Timeout waiting on response_min for message '{}'.".format(message))
        self.on_response_min_sync.clear()

    def _on_response_max(self, value):
        self.last_response_max = value.decode("utf-8")
        self.on_response_max_sync.set()

    def _wait_for_response_max(self, message):
        if not self.on_response_max_sync.wait(1):
            self.fail("Timeout waiting on response_max for message '{}'.".format(message))
        self.on_response_max_sync.clear()

    @classmethod
    def setUpClass(cls):
        cls.config = myconfigtools.read_config(
            os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))+"/tests_unit/config.yaml")
        cls.logger = mylogger.create_logger(cls.config["logger"], __name__)
        cls.logger.info("TestDatapoint - start")

    @classmethod
    def tearDownClass(cls):
        cls.logger.info("TestDatapoint - stop")

    def setUp(self):
        self.mqtt_client = mymqttclient.MyMQTTClient(self.config["mqtt"], self.logger, True)
        self.mqtt_client.connect()
        self.end_time, self.data_set = testdatagenerator.generate_test_data(number_entries=100, time_interval=30)

        self.on_response_avg_sync = Event()
        self.on_response_avg_sync.clear()
        self.last_response_avg = None
        self.on_response_wavg_sync = Event()
        self.on_response_wavg_sync.clear()
        self.last_response_wavg = None
        self.on_response_count_sync = Event()
        self.on_response_count_sync.clear()
        self.last_response_count = None
        self.on_response_min_sync = Event()
        self.on_response_min_sync.clear()
        self.last_response_min = None
        self.on_response_max_sync = Event()
        self.on_response_max_sync.clear()
        self.last_response_max = None

        self.config_methods = {}
        for m in self.config["data-preparation"]["methods"]:
            key = m["name"]
            if key in self.config_methods:
                raise ValueError("method name must be unique ({}).".format(key))
            self.config_methods[key] = m

        try:
            self.config_datapoint = self.config["data-preparation"]["datapoints"][0]
            self.no_data_behavior = NoDataBehavior.get_enum(self.config["data-preparation"]["no_data_behavior"])
        except KeyError:
            raise ValueError("config malformed.")

    def tearDown(self):
        self.mqtt_client.disconnect()

    def test_dp0_init(self):
        self.logger.info("TestDatapoint.test_dp_init ---------------------------------------------")
        dp = DataPoint(self.config_datapoint, self.config_methods, self.mqtt_client, self.logger,
                       self.no_data_behavior)
        self.assertEqual(dp._topic_sub, self.config_datapoint["topic-sub"])
        self.assertEqual(dp._topic_pub_prefix, self.config_datapoint["topic-pub-prefix"])
        self.assertEqual(dp._zero_is_valid, self.config_datapoint["zero_is_valid"])
        self.assertEqual(dp._max_time_window, 300)
        self.assertEqual(len(dp.methods), 5)
        method_types = []
        for m in dp.methods:
            method_types.append(type(m))
        self.assertEqual(len(method_types), 5)
        self.assertIn(Average, method_types)
        self.assertIn(WeightedAverage, method_types)
        self.assertIn(Count, method_types)
        self.assertIn(Maximum, method_types)
        self.assertIn(Minimum, method_types)
        self.assertIsNotNone(dp._data_set)
        self.assertEqual(len(dp._data_set), 0)
        self.assertIsNotNone(dp._lock_data_set)
        self.assertIsNotNone(dp._logger)
        self.assertIsNotNone(dp._mqtt_client)

    def test_dp1_purge(self):
        self.logger.info("TestDatapoint.test_dp_purge ---------------------------------------------")
        dp = DataPoint(self.config_datapoint, self.config_methods, self.mqtt_client, self.logger,
                       self.no_data_behavior)
        dp._data_set = self.data_set
        old_size = len(dp._data_set)
        dp.purge_old_values(self.end_time)
        new_size = len(dp._data_set)
        self.assertLess(new_size, old_size)
        self.assertEqual(new_size, 11)

    def test_dp2_send_data(self):
        self.logger.info("TestDatapoint.test_dp_send_data ---------------------------------------------")
        dp = DataPoint(self.config_datapoint, self.config_methods, self.mqtt_client, self.logger,
                       self.no_data_behavior)
        dp.start()
        for v in self.data_set.values():
            self.mqtt_client.publish(dp._topic_sub, v)
            time.sleep(0.025)
        time.sleep(0.5)
        self.assertEqual(len(dp._data_set), 100)
        dp.stop()

    def test_dp3_algorithms(self):
        self.logger.info("TestDatapoint.test_dp_algorithms ---------------------------------------------")
        dp = DataPoint(self.config_datapoint, self.config_methods, self.mqtt_client, self.logger,
                       self.no_data_behavior)
        for k,v in self.data_set.items():
            dp._data_set[k] = v
        dp.start()
        self.mqtt_client.subscribe(dp._topic_pub_prefix+"avg_5min", self._on_response_avg)
        self.mqtt_client.subscribe(dp._topic_pub_prefix+"wavg_5min", self._on_response_wavg)
        self.mqtt_client.subscribe(dp._topic_pub_prefix+"count_2min", self._on_response_count)
        self.mqtt_client.subscribe(dp._topic_pub_prefix+"min_3min", self._on_response_min)
        self.mqtt_client.subscribe(dp._topic_pub_prefix+"max_3min", self._on_response_max)
        for m in dp.methods:
            m.process(self.end_time)
        self._wait_for_response_avg("avg_5min")
        self._wait_for_response_wavg("wavg_5min")
        self._wait_for_response_count("count_2min")
        self._wait_for_response_min("min_3min")
        self._wait_for_response_max("max_3min")
        self.assertEqual(float(self.last_response_avg), 5)
        self.assertEqual(float(self.last_response_wavg), 3)
        self.assertEqual(int(self.last_response_count), 5)
        self.assertEqual(float(self.last_response_min), 0)
        self.assertEqual(float(self.last_response_max), 6)
        dp.stop()


if __name__ == '__main__':
    unittest.main()
