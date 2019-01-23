
import logging
import sys
import unittest
from lbciagent.LbCIAgent import LbCIAgent
from lbmessaging.exchanges.Common import get_connection
from lbmessaging.exchanges.ContinuousIntegrationExchange import \
    ContinuousIntegrationExchange
from lbmessaging.exchanges.CvmfsDevExchange import CvmfsDevExchange

import json
import os
import threading
import signal

QUEUE_NAME = 'BuildReadyCIAgent'
QUEUE_NAME_ENV = 'EnvKitReadyCIAgent'
QUEUE_NAME_COMMANDS = "CVMFSDevActions"


class TestCvmfsDevMsg(unittest.TestCase):

    def setUp(self):
        self._connection = get_connection(vhost='/lhcb-test')
        self.gateway = LbCIAgent(vhost='/lhcb-test')
        self.broker_reader = ContinuousIntegrationExchange(self._connection)
        self.broker_reader.receive_all_build_ready(QUEUE_NAME)
        self.broker_reader.receive_all_envkit_ready(QUEUE_NAME_ENV)
        self.broker_commands = CvmfsDevExchange(self._connection)
        self.broker_commands.receive_all(QUEUE_NAME_COMMANDS)

    def tearDown(self):
        if self._connection:
            self._connection.close()

    def insertDumpedData(self):
        original = os.path.realpath(__file__).replace('.py', '')
        original = original.replace('.pyc', '')
        if original[-1] == 'c':
            original = original[:len(original)-1]
        filename = original.replace('test_order', 'testCases.json')
        with open(filename, 'r') as row_data:
            data = json.load(row_data)

        for d in data:
            deployment = d.get('deployment', [])
            priority = d.get('priority', None)
            self.broker_reader.send_build_ready(d['slot'], d['build_id'],
                                                d['platform'], d['project'],
                                                deployment=deployment,
                                                priority=priority)
        self.broker_reader.send_envkit_ready('flavour1', 'platform1', 'v1')
        return

    def triggerSingal(self):
        logging.warn("Sending endkill")
        self.gateway.signalHandler()

    def test_order(self):
        """ Check whether a a large sample of builds pass through """
        self.insertDumpedData()
        logging.warn("Starting timer")
        threading.Timer(5, self.triggerSingal).start()
        self.gateway.start()

        # define the order
        order = ['lhcb-head', 'lhcb-2018-patches',
                 'lhcb-gaudi-head', 'lhcb-tdr-test', 'lhcb-run2-patches',
                 'lhcb-gauss-dev', 'lhcb-lcg-dev3', 'lhcb-lcg-dev4',
                 'lhcb-head', 'lhcb-sim09', 'lhcb-2018-patches',
                 'lhcb-gaudi-head', 'lhcb-tdr-test', 'lhcb-run2-patches',
                 'lhcb-gauss-dev', 'lhcb-sim09-upgrade', 'lhcb-2017-patches',
                 'lhcb-2016-patches', 'lhcb-lcg-dev3', 'lhcb-lcg-dev4',
                 'lhcb-gauss-newgen',
                 'lhcb-clang-test', 'lhcb-reco14-patches',
                 'lhcb-stripping21-patches', 'lhcb-stripping24-patches']

        # New connection to get the results

        results = self.broker_commands.receive_all(QUEUE_NAME_COMMANDS)
        res_parsed = []
        self.assertEqual(results[0].body.command, 'env_kit_installer')
        for r in results[1:]:
            if len(res_parsed) == 0 or res_parsed[-1] != r.body.arguments[0]:
                res_parsed.append(r.body.arguments[0])

        for i in range(len(order)):
            if order[i] != res_parsed[i]:
                self.fail("Priorities are not correct")

if __name__ == "__main__":
    logging.basicConfig(stream=sys.stderr)
    logging.getLogger().setLevel(logging.WARNING)
    unittest.main()
