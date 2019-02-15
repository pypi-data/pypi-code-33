import unittest
import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import time
from pelops import mylogger, mymqttclient, myconfigtools
from alcathous.datapointmanager import DataPointManager
from alcathous.nodatabehavior import NoDataBehavior


# https://stackoverflow.com/questions/3173320/text-progress-bar-in-the-console
# Print iterations progress
def printProgressBar (iteration, total, prefix = '', suffix = '', decimals = 1, length = 100, fill = '█', msg=None):
    """
    Call in a loop to create terminal progress bar
    @params:
        iteration   - Required  : current iteration (Int)
        total       - Required  : total iterations (Int)
        prefix      - Optional  : prefix string (Str)
        suffix      - Optional  : suffix string (Str)
        decimals    - Optional  : positive number of decimals in percent complete (Int)
        length      - Optional  : character length of bar (Int)
        fill        - Optional  : bar fill character (Str)
    """
    percent = ("{0:." + str(decimals) + "f}").format(100 * (iteration / float(total)))
    filledLength = int(length * iteration // total)
    bar = fill * filledLength + '-' * (length - filledLength)
    if msg is None:
        print('\r%s |%s| %s%% %s' % (prefix, bar, percent, suffix), end = '\r')
    else:
        print('\r%s |%s| %s%% %s %s' % (prefix, bar, percent, suffix, msg), end='\r')
    # Print New Line on Complete
    if iteration == total:
        print()


class TestDatapointManager(unittest.TestCase):
    def _create_handler(self, id):
        self.logger.info("TestDatapointManager._create_handler - created handler for topic {}.".format(id))
        def _func(message):
            value = message.decode("utf-8")
            self.received_messages[id].append((time.time(), value))
        return _func

    def _add_handler(self, topic):
        _func = self._create_handler(topic)
        self.mqtt_client.subscribe(topic, _func)
        self.received_messages[topic] = []

    def init_handler(self, data_point_list):
        for dp in data_point_list:
            self._add_handler(dp._topic_sub)
            for m in dp.methods:
                self._add_handler(m._topic)

    @classmethod
    def setUpClass(cls):
        cls.config = myconfigtools.read_config(
            os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))+"/tests_unit/config.yaml")
        cls.logger = mylogger.create_logger(cls.config["logger"], __name__)
        cls.logger.info("TestDatapointManager - start")

    @classmethod
    def tearDownClass(cls):
        cls.logger.info("TestDatapointManager - stop")

    def setUp(self):
        self.mqtt_client = mymqttclient.MyMQTTClient(self.config["mqtt"], self.logger, True)
        self.mqtt_client.connect()
        self.received_messages = {}

    def tearDown(self):
        self.mqtt_client.disconnect()

    def test_dpm0_init(self):
        self.logger.info("TestDatapointManager.test_dpm_init ---------------------------------------------")
        dpm = DataPointManager(self.config, self.mqtt_client, self.logger)
        self.assertEqual(dpm._no_data_behavior, NoDataBehavior.LAST_VALID)
        self.assertEqual(dpm._update_cycle, 30)
        self.assertEqual(dpm._worker._number, 2)
        self.assertEqual(len(dpm._data_points), 2)
        self.assertEqual(len(dpm._purges), 2)
        self.assertEqual(len(dpm._processes), 7)
        process_names = []
        for dp in dpm._data_points:
            for m in dp.methods:
                process_names.append(m.name)
        process_names = sorted(process_names)
        self.assertListEqual(process_names, ['avg_5min', 'avg_5min', 'count_2min', 'max_3min', 'min_3min', 'wavg_5min', 'wavg_5min'])
        self.assertEqual(dpm._data_points[0]._topic_sub, "/test/0/raw")
        self.assertEqual(dpm._data_points[1]._topic_sub, "/test/1/raw")
        self.assertEqual(dpm._data_points[0]._topic_pub_prefix, "/test/0/aggregated/")
        self.assertEqual(dpm._data_points[1]._topic_pub_prefix, "/test/1/aggregated/")

    def test_dpm1_startstop(self):
        self.logger.info("TestDatapointManager.test_dpm_startstop ---------------------------------------------")
        dpm = DataPointManager(self.config, self.mqtt_client, self.logger)
        self.assertEqual(len(dpm._worker._list), 0)
        self.assertEqual(len(self.mqtt_client._topic_handler), 0)
        dpm.start()
        self.assertEqual(len(dpm._worker._list), 2)
        self.assertEqual(len(self.mqtt_client._topic_handler), 2)
        dpm.stop()
        self.assertEqual(len(dpm._worker._list), 0)
        self.assertEqual(len(self.mqtt_client._topic_handler), 0)

    def test_dpm2_full(self):
        self.logger.info("TestDatapointManager.test_dpm_full ---------------------------------------------")
        print("TestDatapointManager.test_dpm_full - this test takes approx. 12 minutes to complete.")
        start_time = time.time()
        dpm = DataPointManager(self.config, self.mqtt_client, self.logger)
        self.init_handler(dpm._data_points)
        dpm.start()
        time.sleep(5)
        printProgressBar(0, 72, prefix='Progress:', suffix='Complete', length=100)
        for value in range(0, 36):
            for dp in dpm._data_points:
                self.mqtt_client.publish(dp._topic_sub, value)
            time.sleep(10)
            diff = (time.time()-start_time)/60
            diff = "{:10.1f} min".format(diff)
            printProgressBar(value+1, 72, prefix='Progress:', suffix='Complete', length=100, msg=diff)
        for value in range(36, 72):
            time.sleep(10)
            diff = (time.time()-start_time)/60
            diff = "{:10.1f} min".format(diff)
            printProgressBar(value+1, 72, prefix='Progress:', suffix='Complete', length=100, msg=diff)
        dpm.stop()
        self.assertEqual(len(self.received_messages["/test/0/aggregated/wavg_5min"]), 25)
        self.assertEqual(len(self.received_messages["/test/1/aggregated/wavg_5min"]), 25)
        self.assertEqual(len(self.received_messages["/test/0/aggregated/avg_5min"]), 25)
        self.assertEqual(len(self.received_messages["/test/1/aggregated/avg_5min"]), 25)
        self.assertEqual(len(self.received_messages["/test/0/aggregated/count_2min"]), 25)
        self.assertEqual(len(self.received_messages["/test/0/aggregated/min_3min"]), 25)
        self.assertEqual(len(self.received_messages["/test/0/aggregated/max_3min"]), 25)

        self.assertAlmostEqual(float(self.received_messages["/test/0/aggregated/wavg_5min"][24][1]), 34.43, delta=0.1)
        self.assertAlmostEqual(float(self.received_messages["/test/1/aggregated/wavg_5min"][24][1]), 34.43, delta=0.1)
        self.assertAlmostEqual(float(self.received_messages["/test/0/aggregated/avg_5min"][24][1]), 34.0, delta=0.1)
        self.assertAlmostEqual(float(self.received_messages["/test/1/aggregated/avg_5min"][24][1]), 34.0, delta=0.1)
        self.assertAlmostEqual(float(self.received_messages["/test/0/aggregated/count_2min"][24][1]), 0, delta=0.1)
        self.assertAlmostEqual(float(self.received_messages["/test/0/aggregated/min_3min"][24][1]), 33.0, delta=0.1)
        self.assertAlmostEqual(float(self.received_messages["/test/0/aggregated/max_3min"][24][1]), 35.0, delta=0.1)


if __name__ == '__main__':
    unittest.main()

