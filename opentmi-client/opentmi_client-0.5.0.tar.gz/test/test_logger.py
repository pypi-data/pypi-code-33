# pylint: disable=missing-docstring

import unittest
from logging import Logger, DEBUG
from opentmi_client import OpenTmiClient
from opentmi_client.utils import get_logger

class TestLogger(unittest.TestCase):
    def test_default_logger(self):
        logger = get_logger()
        self.assertIsInstance(logger, Logger)
        self.assertEqual(len(logger.handlers), 1)

    def test_null_logger(self):
        logger = get_logger(name="new", level=None)
        self.assertIsInstance(logger, Logger)
        self.assertEqual(len(logger.handlers), 1)

    def test_set_logger(self):
        client = OpenTmiClient()
        client.set_logger(get_logger(level=DEBUG))


if __name__ == '__main__':
    unittest.main()
