import unittest
import os
import requests
import uuid
import time

from collections import defaultdict
from logging import Logger

from generic_dao import GenericDAO

class TestGenericDAO(unittest.TestCase):
    def setUp(self):
        stash = defaultdict(str)
        stash["token"] = os.getenv("GITHUB_TOKEN")
        stash["path"] = os.getenv("GITHUB_PATH")
        stash["uuid"] = str(uuid.uuid1())
        self.generic_dao = GenericDAO(stash)

    def test_read(self):
        self.assertIsNotNone(self.generic_dao.read("README.md"))

    def test_create(self):
        self.generic_dao.create("test" + str(time.time()), "test" + str(time.time()))

    def test_update(self):
        timestamp = str(time.time())
        self.generic_dao.create("test" + timestamp, "test" + timestamp)
        self.generic_dao.update("test" + timestamp, "test_update")

    def test_create_or_update(self):
        timestamp = str(time.time())
        self.generic_dao.create_or_update("test" + timestamp, "test" + timestamp)
        self.generic_dao.create_or_update("test" + timestamp, "test_create_or_update")

    def test_delete(self):
        timestamp = str(time.time())
        self.generic_dao.create("test" + timestamp, "test_delete")
        self.generic_dao.delete("test" + timestamp)

if __name__ == "__main__":
    unittest.main()