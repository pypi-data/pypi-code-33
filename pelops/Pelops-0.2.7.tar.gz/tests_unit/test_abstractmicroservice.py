import unittest
import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from pelops.mymqttclient import MyMQTTClient
from pelops.myconfigtools import read_config
from pelops.mylogger import create_logger
from pelops.abstractmicroservice import AbstractMicroservice
import threading
import time


class TestService(AbstractMicroservice):
    _version = 1
    start_topic = None
    stop_topic = None
    stop_me_topic = None

    def __init__(self, config, mqtt_client=None, logger=None):
        AbstractMicroservice.__init__(self, config, "test", mqtt_client, logger, logger_name="service")
        self.start_topic = self._config["start"]
        self.stop_topic = self._config["stop"]
        self.stop_me_topic = self._config["stop-me"]

    def _stop_me_handler(self, message):
        self._logger.info("received stop-me signal on topic '{}'".format(self.stop_me_topic))
        self.asyncstop()

    def _start(self):
        self._logger.info("sending 'start' to topic '{}'".format(self.start_topic))
        self._mqtt_client.subscribe(self.stop_me_topic, self._stop_me_handler)
        self._mqtt_client.publish(self.start_topic, "start")

    def _stop(self):
        self._logger.info("sending 'stop' to topic '{}'".format(self.stop_topic))
        self._logger.debug("_stop - 1")
        self._mqtt_client.unsubscribe(self.stop_me_topic, self._stop_me_handler)
        self._logger.debug("_stop - 2")
        self._mqtt_client.publish(self.stop_topic, "stop")
        self._logger.debug("_stop - 3")

    @classmethod
    def _get_description(cls):
        return "TestService"

    @classmethod
    def _get_schema(cls):
        schema = {
            "test": {
                "description": "test configuration",
                "type": "object",
                "properties": {
                    "start": {
                        "description": "start",
                        "type": "string",
                    },
                    "stop": {
                        "description": "stop",
                        "type": "string",
                    },
                    "stop-me": {
                        "description": "stop-me",
                        "type": "string"
                    }
                },
                "required": ["start", "stop", "stop-me"]
            }
        }
        return schema


class TestAbstractMicroservice(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.filename = os.path.abspath(os.path.join(os.path.dirname(__file__), '..')) + "/tests_unit/config_test.yaml"
        cls.main_config = read_config(cls.filename)
        cls.logger = create_logger(cls.main_config["logger"], "test")
        cls.logger.info("start ==============================================")

    @classmethod
    def tearDownClass(cls):
        cls.logger.info("end ================================================")

    def setUp(self):
        self.logger.info("----------------------------------------------------")
        self.mqttclient = MyMQTTClient(self.main_config["mqtt"], self.logger, True)
        self.mqttclient.connect()

    def tearDown(self):
        self.mqttclient.disconnect()

    def test_0init(self):
        t = TestService(self.main_config, self.mqttclient, self.logger)
        self.assertIsNotNone(t)

    def test_1start_stop(self):
        a = threading.Event()
        a.clear()
        b = threading.Event()
        b.clear()

        def recv_a(message):
            a.set()

        def recv_b(message):
            b.set()

        self.mqttclient.subscribe(self.main_config["test"]["start"], recv_a)
        self.mqttclient.subscribe(self.main_config["test"]["stop"], recv_b)

        t = TestService(self.main_config, self.mqttclient, self.logger)
        self.assertIsNotNone(t)
        self.assertFalse(t._stop_service.is_set())
        self.assertTrue(t._is_stopped.is_set())
        time.sleep(0.5)

        self.assertFalse(a.is_set())
        self.assertFalse(b.is_set())

        t.start()

        self.assertFalse(t._stop_service.is_set())
        self.assertFalse(t._is_stopped.is_set())

        a.wait(0.5)
        b.wait(0.5)
        self.assertTrue(a.is_set())
        self.assertFalse(b.is_set())
        a.clear()

        t.stop()
        self.assertTrue(t._stop_service.is_set())
        a.wait(0.5)
        b.wait(0.5)
        self.assertFalse(a.is_set())
        self.assertTrue(b.is_set())
        self.assertTrue(t._is_stopped.is_set())

    def test_2run(self):
        a = threading.Event()
        a.clear()
        b = threading.Event()
        b.clear()

        def recv_a(message):
            a.set()

        def recv_b(message):
            b.set()

        self.mqttclient.subscribe(self.main_config["test"]["start"], recv_a)
        self.mqttclient.subscribe(self.main_config["test"]["stop"], recv_b)

        t = TestService(self.main_config, mqtt_client=None, logger=self.logger)
        thread = threading.Thread(target=t.run)
        self.assertIsNotNone(t)
        self.assertFalse(t._stop_service.is_set())
        self.assertTrue(t._is_stopped.is_set())
        self.assertFalse(t._is_started.is_set())
        self.assertFalse(a.is_set())
        self.assertFalse(b.is_set())

        thread.start()
        t._is_started.wait(1)
        self.assertTrue(t._is_started.is_set())
        self.assertFalse(t._stop_service.is_set())
        self.assertFalse(t._is_stopped.is_set())

        a.wait(1)
        self.assertTrue(a.is_set())

        t.stop()
        t._is_stopped.wait(1)
        self.assertTrue(t._stop_service.is_set())
        self.assertTrue(t._is_stopped.is_set())
        self.assertFalse(t._is_started.is_set())

        b.wait(1)
        self.assertTrue(b.is_set())

        thread.join()

    def test_3standalone(self):
        a = threading.Event()
        a.clear()
        b = threading.Event()
        b.clear()

        def recv_a(message):
            a.set()

        def recv_b(message):
            b.set()

        self.mqttclient.subscribe(self.main_config["test"]["start"], recv_a)
        self.mqttclient.subscribe(self.main_config["test"]["stop"], recv_b)

        thread = threading.Thread(target=TestService.standalone, args=[("-c", self.filename)])
        thread.start()
        self.logger.info(" ---- started testservice ---- ")
        a.wait(1)
        self.assertTrue(a.is_set())
        self.assertFalse(b.is_set())
        self.mqttclient.publish(self.main_config["test"]["stop-me"], "")
        b.wait(1)
        self.assertTrue(b.is_set())
        thread.join()


if __name__ == '__main__':
    unittest.main()
