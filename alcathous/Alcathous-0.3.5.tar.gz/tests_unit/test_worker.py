import unittest
import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from pelops import mylogger, mymqttclient, myconfigtools
from alcathous.worker import Worker
import time


class TestWorker(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        config = myconfigtools.read_config(
            os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))+"/tests_unit/config.yaml")
        cls.logger = mylogger.create_logger(config["logger"], __name__)
        cls.logger.info("TestWorker - start")
        cls.config = config["data-preparation"]

    @classmethod
    def tearDownClass(cls):
        cls.logger.info("TestWorker - stop")

    def test_worker0_init(self):
        worker = Worker(self.config["number_worker"], self.logger)
        self.assertEqual(worker._number, 2)
        self.assertIsNotNone(worker.queue)
        self.assertIsNotNone(worker._logger)
        self.assertIsNotNone(worker._list)
        self.assertEqual(len(worker._list), 0)

    def test_worker1_start_stop(self):
        worker = Worker(self.config["number_worker"], self.logger)
        worker.start()
        self.assertEqual(len(worker._list), 2)
        worker.stop()
        self.assertEqual(len(worker._list), 0)

    def test_worker2_queue(self):
        worker = Worker(self.config["number_worker"], self.logger)
        worker.start()
        start_time = time.time()
        for i in range(4):
            worker.queue.put((time.sleep, 1))
        worker.stop()  # must be called before taking time
        stop_time = time.time()
        diff_time = stop_time - start_time
        self.assertLess(diff_time, 3)  # two workers are processing 4*sleep(1) - it should be done in close to 2 ...
        self.assertGreater(diff_time, 2)  # it must take at least 2 seconds ...


if __name__ == '__main__':
    unittest.main()