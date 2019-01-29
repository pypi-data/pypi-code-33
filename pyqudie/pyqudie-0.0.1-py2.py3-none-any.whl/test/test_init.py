"""
Unit Tests
function: Constructor
"""

import unittest
import sys
import testconfig as config

sys.path.append("..")

from Mongo import Mongo


class TestInit(unittest.TestCase):

    def test_init1(self):
        test = Mongo.Mongo(config.database_host, config.database_port, True, config.database_username,
                           config.database_password, "admin")
        self.assertTrue(isinstance(test, Mongo.Mongo))
        self.assertEquals(test.url, "mongodb://{}:{}@{}:{}/".format(config.database_username, config.database_password,
                                                                     config.database_host, config.database_port))

    # def test_init2(self):
    #     test = Mongo.Mongo(config.database_host, config.database_port, False, database = "admin")
    #     self.assertTrue(isinstance(test, Mongo.Mongo))
    #     self.assertEquals(test.url, "mongodb://127.0.0.1:27017/")

    # def test_init3(self):
    #     test = Mongo.Mongo()
    #     self.assertTrue(isinstance(test, Mongo.Mongo))
    #     self.assertEquals(test.url, "mongodb://127.0.0.1:27017/")

    def test_init3(self):
        try:
            Mongo.Mongo("1.1.1.1", 27017, True, config.database_username, config.database_password, "admin")
        except ImportError as err:
            self.assertEquals(err.message, "Authentication Required or Connection Error!")
        else:
            raise AssertionError

    def test_init4(self):
        try:
            Mongo.Mongo(123, 456, 789)
        except ImportError as err:
            self.assertEquals(err.message, "Invalid Arguments!")
        else:
            raise AssertionError

    # def test_init5(self):
    #     try:
    #         Mongo.Mongo()
    #     except ImportError as err:
    #         self.assertEquals(err.message, "Authentication Required or Connection Error!")
    #     else:
    #         raise AssertionError

    def test_init6(self):
        try:
            Mongo.Mongo(config.database_host, config.database_port, True, config.database_username,
                           config.database_password, "asdasdasd")
        except ImportError as err:
            self.assertEquals(err.message, "No such Database!")
        else:
            raise AssertionError
