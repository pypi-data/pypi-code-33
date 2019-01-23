
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

QUEUE_NAME = 'build_ready_gateway'
QUEUE_NAME_COMMANDS = "test_cvmfs_actions_queue"


class TestCvmfsDevMsg(unittest.TestCase):

    def setUp(self):
        self._connection = get_connection(vhost='/lhcb-test')
        self.gateway = LbCIAgent(build_queue_name=QUEUE_NAME,
                                 connection=self._connection)
        self.broker_reader = ContinuousIntegrationExchange(self._connection)
        self.broker_reader.receive_all(QUEUE_NAME)

    def tearDown(self):
        if self._connection:
            self._connection.close()

    def insertDumpedData(self):
        original = os.path.realpath(__file__).replace('.py',
                                                      '').replace('.pyc', '')
        filename = original.replace('TestGateway', 'testCases.json')
        with open(filename, 'r') as row_data:
            data = json.load(row_data)

        for d in data:
            deployment = d.get('deployment', [])
            priority = d.get('priority', None)
            self.broker_reader.send_build_ready(d['slot'], d['build_id'],
                                                d['platform'], d['project'],
                                                deployment=deployment,
                                                priority=priority)
        return

    def triggerSingal(self):
        for t in threading.enumerate():
            if t != threading.current_thread:
                os.kill(os.getpid(), signal.SIGINT)

    def test_BigData(self):
        """ Check whether a a large sample of builds pass through """
        self.insertDumpedData()
        threading.Timer(50, self.triggerSingal).start()
        self.gateway.start()

        # define the order
        order = ['lhcb-head', 'lhcb-gaudi-merge', 'lhcb-future',
                 'lhcb-2017-patches', 'lhcb-2018-patches', 'lhcb-gaudi-head',
                 'lhcb-2016-patches', 'lhcb-gauss-cmake', 'lhcb-gauss-dev',
                 'lhcb-sim09-upgrade', 'lhcb-prerelease', 'lhcb-lcg-dev3',
                 'lhcb-lcg-dev4', 'lhcb-reco14-patches',
                 'lhcb-stripping21-patches', 'lhcb-gauss-newgen',
                 'lhcb-gauss-newgen2', 'lhcb-stripping24-patches']

        # New connection to get the results

        self._connection = get_connection(vhost='/lhcb-test')
        self.broker_commands = CvmfsDevExchange(self._connection)
        results = self.broker_commands.receive_all(QUEUE_NAME_COMMANDS)
        res_parsed = []
        for r in results:
            if len(res_parsed) == 0 or res_parsed[-1] != r.body.arguments[0]:
                res_parsed.append(r.body.arguments[0])
        index = -1
        for r in res_parsed:
            tmp_index = order.index(r)
            if tmp_index > index:
                index = tmp_index
            else:
                self.fail("Priorities are not correct")

if __name__ == "__main__":
    logging.basicConfig(stream=sys.stderr)
    logging.getLogger().setLevel(logging.WARNING)
    unittest.main()
