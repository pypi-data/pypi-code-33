"""
Unit Tests
function: insert
"""

import unittest
import sys
import pymongo
import testconfig as config

sys.path.append("..")

from Mongo import Mongo


class TestInsert(unittest.TestCase):

    def setUp(self):

        Client = pymongo.MongoClient("mongodb://{}:{}@{}:{}/".format(config.database_username, config.database_password,
                                                                     config.database_host, config.database_port))
        Database = Client['test']
        Collection = Database['test']

        Collection.delete_many({})
        print "Data in database has been cleared."

    def test_insert1(self):

        test = Mongo.Mongo(config.database_host, config.database_port, True,
                           config.database_username, config.database_password)
        result = test.insert("test", {"test": "test1", "test2": "test3"})

        self.assertEquals(len(result), 1)

        datas = self.getData()

        self.assertEquals(datas[0]['test'], "test1")
        self.assertEquals(datas[0]['test2'], "test3")

    def test_insert2(self):

        test = Mongo.Mongo(config.database_host, config.database_port, True,
                           config.database_username, config.database_password)
        result = test.insert("test", [{"test": "test1", "test2": "test3"}, {"test": "asdf", "test2": "qwe"}])

        self.assertEquals(len(result), 2)

        datas = self.getData()

        self.assertEquals(datas[0]['test'], "test1")
        self.assertEquals(datas[0]['test2'], "test3")
        self.assertEquals(datas[1]['test'], "asdf")
        self.assertEquals(datas[1]['test2'], "qwe")

    def test_insert3(self):

        test = Mongo.Mongo(config.database_host, config.database_port, True,
                           config.database_username, config.database_password)

        try:
            result = test.insert("tes", {"id": 124})
        except RuntimeError as err:
            self.assertEquals(err.message, "No such Collection!")
        else:
            raise AssertionError

    def test_insert4(self):

        test = Mongo.Mongo(config.database_host, config.database_port, True,
                           config.database_username, config.database_password)

        try:
            result = test.insert(123, {"id": 124})
        except TypeError as err:
            self.assertEquals(err.message, "Invalid Collection!")
        else:
            raise AssertionError

    def test_insert5(self):

        test = Mongo.Mongo(config.database_host, config.database_port, True,
                           config.database_username, config.database_password)

        try:
            result = test.insert("test", "{'id': 124}")
        except TypeError as err:
            self.assertEquals(err.message, "Invalid Insert Object!")
        else:
            raise AssertionError

    def test_insert6(self):

        test = Mongo.Mongo(config.database_host, config.database_port, True,
                           config.database_username, config.database_password)

        try:
            result = test.insert("test", [{'id': 124}, "sdf"])
        except TypeError as err:
            self.assertEquals(err.message, "Invalid Insert Object!")
        else:
            raise AssertionError

    def getData(self):

        Client = pymongo.MongoClient("mongodb://{}:{}@{}:{}/".format(config.database_username, config.database_password,
                                                                     config.database_host, config.database_port))
        Database = Client['test']
        Collection = Database['test']
        Cursor = Collection.find({})
        datas = []

        for data in Cursor:
            datas.append(data)

        return datas

    def tearDown(self):

        Client = pymongo.MongoClient("mongodb://{}:{}@{}:{}/".format(config.database_username, config.database_password,
                                                                     config.database_host, config.database_port))
        Database = Client['test']
        Collection = Database['test']

        Collection.delete_many({})
        print "Test data set in database has been cleared."
