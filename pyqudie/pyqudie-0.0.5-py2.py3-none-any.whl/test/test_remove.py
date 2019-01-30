"""
Unit Tests
function: remove
"""

import unittest
import sys
import pymongo
import testconfig as config

sys.path.append("..")

from Mongo import Mongo


class TestRemove(unittest.TestCase):

    def setUp(self):

        Client = pymongo.MongoClient("mongodb://{}:{}@{}:{}/".format(config.database_username, config.database_password,
                                                                     config.database_host, config.database_port))
        Database = Client['test']
        Collection = Database['test']

        Collection.delete_many({})
        print "Data in database has been cleared."
        Collection.insert_many([
            {"test1": "asdf", "test2": "asdasd"},
            {"test1": "qwe", "test2": "qaq"},
            {"test1": "asdf", "test2": "qwert"}
        ])

    def test_remove1(self):

        test = Mongo.Mongo(config.database_host, config.database_port, True,
                           config.database_username, config.database_password)
        collection = "test"
        removeQuery = {"test1": "asdf"}
        result = test.remove(collection, removeQuery)

        self.assertEquals(result, 1)

        datas = self.getData()

        self.assertEquals(len(datas), 2)
        self.assertEquals(datas[0]['test1'], "qwe")
        self.assertEquals(datas[0]['test2'], "qaq")
        self.assertEquals(datas[1]['test1'], "asdf")
        self.assertEquals(datas[1]['test2'], "qwert")

    def test_remove2(self):

        test = Mongo.Mongo(config.database_host, config.database_port, True,
                           config.database_username, config.database_password)
        collection = "test"
        removeQuery = {"test1": "asdf"}
        result = test.remove(collection, removeQuery, removeMany = True)

        self.assertEquals(result, 2)

        datas = self.getData()

        self.assertEquals(len(datas), 1)
        self.assertEquals(datas[0]['test1'], "qwe")
        self.assertEquals(datas[0]['test2'], "qaq")

    def test_remove3(self):

        test = Mongo.Mongo(config.database_host, config.database_port, True,
                           config.database_username, config.database_password)
        collection = "testqwer"
        removeQuery = {"test1": "asdf"}

        try:
            test.remove(collection, removeQuery)
        except RuntimeError as err:
            self.assertEquals(err.message, "No such Collection!")
        else:
            raise AssertionError

    def test_remove4(self):

        test = Mongo.Mongo(config.database_host, config.database_port, True,
                           config.database_username, config.database_password)
        collection = 123
        removeQuery = {"test1": "asdf"}

        try:
            test.remove(collection, removeQuery)
        except TypeError as err:
            self.assertEquals(err.message, "Invalid Collection!")
        else:
            raise AssertionError

    def test_remove5(self):

        test = Mongo.Mongo(config.database_host, config.database_port, True,
                           config.database_username, config.database_password)
        collection = "test"
        removeQuery = "{'tet':'test'}"

        try:
            test.remove(collection, removeQuery)
        except TypeError as err:
            self.assertEquals(err.message, "Invalid Remove Query!")
        else:
            raise AssertionError

    def test_remove6(self):

        test = Mongo.Mongo(config.database_host, config.database_port, True,
                           config.database_username, config.database_password)
        collection = "test"
        removeQuery = {"test1": "asdf"}

        try:
            test.remove(collection = collection, removeQuery = removeQuery, removeAllConfirm = 123)
        except TypeError as err:
            self.assertEquals(err.message, "Invalid Remove Option!")
        else:
            raise AssertionError

    def test_remove7(self):

        test = Mongo.Mongo(config.database_host, config.database_port, True,
                           config.database_username, config.database_password)
        collection = "test"
        removeQuery = {"test1": "asdf"}

        try:
            test.remove(collection = collection, removeQuery = removeQuery, removeMany = "asdf")
        except TypeError as err:
            self.assertEquals(err.message, "Invalid Remove Option!")
        else:
            raise AssertionError

    def test_remove8(self):

        test = Mongo.Mongo(config.database_host, config.database_port, True,
                           config.database_username, config.database_password)
        collection = "test"
        removeQuery = {}

        try:
            test.remove(collection = collection, removeQuery = removeQuery)
        except RuntimeError as err:
            self.assertEquals(err.message, "Remove All not Confirmed!")
        else:
            raise AssertionError

    def test_remove9(self):

        test = Mongo.Mongo(config.database_host, config.database_port, True,
                           config.database_username, config.database_password)
        collection = "test"
        removeQuery = {}

        result = test.remove(collection = collection, removeQuery = removeQuery, removeAllConfirm = True)

        self.assertEquals(result, 3)

        datas = self.getData()

        self.assertEquals(len(datas), 0)

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
