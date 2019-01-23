import logging
import sys
import unittest

from lbmessaging.services.CVMFSNightliesService import CVMFSNightliesService
from lbmessaging.exchanges.ContinuousIntegrationExchange \
    import ContinuousIntegrationExchange
from lbmessaging.exchanges.test import get_test_connection


QUEUE_NAME = "test_build_ready_queue"


class TestLbCIService(unittest.TestCase):

    def setUp(self):
        channel = get_test_connection().channel()
        broker = ContinuousIntegrationExchange(channel)
        broker.receive_all(QUEUE_NAME)

    def tearDown(self):
        pass

    def test_services(self):
        srv = CVMFSNightliesService(vhost='/lhcb-test')
        slot = "slot1"
        build_id = "1"
        platform = "x86_64-centos7-gcc62-opt"
        project = "project1"
        srv.send_build_ready(slot, build_id, platform, project)
        tmp = srv.receive_build_ready(QUEUE_NAME)
        self.assertEqual(slot, tmp.body.slot)
        self.assertEqual(build_id, tmp.body.build_id)
        self.assertEqual(platform, tmp.body.platform)
        self.assertEqual(project, tmp.body.project)


if __name__ == "__main__":
    logging.basicConfig(stream=sys.stderr)
    logging.getLogger().setLevel(logging.WARNING)
    unittest.main()
