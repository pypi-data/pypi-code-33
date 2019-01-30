"""
Unit Tests
function: find
"""

import unittest
import sys
import pymongo
import testconfig as config

sys.path.append("..")

from pyqudie import Mongo
from pyqudie.MongoExceptions import *


class TestFind(unittest.TestCase):

    def setUp(self):

        Client = pymongo.MongoClient("mongodb://{}:{}@{}:{}/".format(config.database_username, config.database_password,
                                                                     config.database_host, config.database_port))
        Database = Client['test']
        Collection = Database['test']

        testList = [
            {
                "id": 123,
                "name": "asd",
                "asd": "asdasd"
            },
            {
                "id": 456,
                "name": "asdf",
                "asd": "asdf"
            }
        ]

        result = Collection.insert_many(testList)
        print result.inserted_ids

    def test_find1(self):

        test = Mongo.Mongo(config.database_host, config.database_port, True,
                           config.database_username, config.database_password)
        result = test.find("test", {})

        self.assertEquals(len(result), 2)
        self.assertEquals(result[0]['id'], 123)
        self.assertEquals(result[0]['name'], "asd")
        self.assertEquals(result[0]['asd'], "asdasd")
        self.assertEquals(result[1]['id'], 456)
        self.assertEquals(result[1]['name'], "asdf")
        self.assertEquals(result[1]['asd'], "asdf")

    def test_find2(self):

        test = Mongo.Mongo(config.database_host, config.database_port, True,
                           config.database_username, config.database_password)
        result = test.find("test", {"id": 123})

        self.assertEquals(len(result), 1)
        self.assertEquals(result[0]['id'], 123)
        self.assertEquals(result[0]['name'], "asd")
        self.assertEquals(result[0]['asd'], "asdasd")

    def test_find3(self):

        test = Mongo.Mongo(config.database_host, config.database_port, True,
                           config.database_username, config.database_password)
        result = test.find("test", {"id": 124})

        self.assertEquals(len(result), 0)

    def test_find4(self):

        test = Mongo.Mongo(config.database_host, config.database_port, True,
                           config.database_username, config.database_password)

        try:
            test.find("tes", {"id": 124})
        except InvalidCollectionException as err:
            self.assertEquals(err.message, "Invalid Collection!")
        else:
            raise AssertionError

    def test_find5(self):

        test = Mongo.Mongo(config.database_host, config.database_port, True,
                           config.database_username, config.database_password)

        try:
            test.find(123, {"id": 124})
        except InvalidCollectionException as err:
            self.assertEquals(err.message, "Invalid Collection!")
        else:
            raise AssertionError

    def test_find6(self):

        test = Mongo.Mongo(config.database_host, config.database_port, True,
                           config.database_username, config.database_password)

        try:
            test.find("test", "asd")
        except InvalidQueryObjectException as err:
            self.assertEquals(err.message, "Invalid Query Object!")
        else:
            raise AssertionError

    def tearDown(self):
        Client = pymongo.MongoClient("mongodb://{}:{}@{}:{}/".format(config.database_username, config.database_password,
                                                                     config.database_host, config.database_port))
        Database = Client['test']
        Collection = Database['test']

        Collection.delete_many({})
        print "Test data set in database has been cleared."
