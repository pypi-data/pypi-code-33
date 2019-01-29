"""
Unit Tests
function: Update
"""

import unittest
import sys
import pymongo
import testconfig as config

sys.path.append("..")

from Mongo import Mongo


class TestUpdate(unittest.TestCase):

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

    def test_update1(self):

        test = Mongo.Mongo(config.database_host, config.database_port, True,
                           config.database_username, config.database_password)
        collection = "test"
        updateQuery = {"test1": "asdf"}
        updateDict = {"$set": {"test1": "12345"}}
        result = test.update(collection, updateQuery, updateDict)

        self.assertEquals(result, 1)

        datas = self.getData()

        self.assertEquals(len(datas), 3)
        self.assertEquals(datas[0]['test1'], "12345")
        self.assertEquals(datas[1]['test1'], "qwe")
        self.assertEquals(datas[1]['test2'], "qaq")
        self.assertEquals(datas[2]['test1'], "asdf")
        self.assertEquals(datas[2]['test2'], "qwert")

    def test_update2(self):

        test = Mongo.Mongo(config.database_host, config.database_port, True,
                           config.database_username, config.database_password)
        collection = "test"
        updateQuery = {"test1": "asdf"}
        updateDict = {"$set": {"test1": "12345"}}
        result = test.update(collection, updateQuery, updateDict, updateMany = True)

        self.assertEquals(result, 2)

        datas = self.getData()

        self.assertEquals(len(datas), 3)
        self.assertEquals(datas[0]['test1'], "12345")
        self.assertEquals(datas[1]['test1'], "qwe")
        self.assertEquals(datas[1]['test2'], "qaq")
        self.assertEquals(datas[2]['test1'], "12345")

    def test_update3(self):

        test = Mongo.Mongo(config.database_host, config.database_port, True,
                           config.database_username, config.database_password)
        collection = "testqwer"
        updateQuery = {"test1": "asdf"}
        updateDict = {"$set": {"test1": "12345"}}

        try:
            test.update(collection, updateQuery, updateDict)
        except RuntimeError as err:
            self.assertEquals(err.message, "No such Collection!")
        else:
            raise AssertionError

    def test_update4(self):

        test = Mongo.Mongo(config.database_host, config.database_port, True,
                           config.database_username, config.database_password)
        collection = 1234
        updateQuery = {"test1": "asdf"}
        updateDict = {"$set": {"test1": "12345"}}

        try:
            test.update(collection, updateQuery, updateDict)
        except TypeError as err:
            self.assertEquals(err.message, "Invalid Collection!")
        else:
            raise AssertionError

    def test_update5(self):

        test = Mongo.Mongo(config.database_host, config.database_port, True,
                           config.database_username, config.database_password)
        collection = "test"
        updateQuery = "asdasd"
        updateDict = {"$set": {"test1": "12345"}}

        try:
            test.update(collection, updateQuery, updateDict)
        except TypeError as err:
            self.assertEquals(err.message, "Invalid Update Query!")
        else:
            raise AssertionError

    def test_update6(self):

        test = Mongo.Mongo(config.database_host, config.database_port, True,
                           config.database_username, config.database_password)
        collection = "test"
        updateQuery = {"test1": "asdf"}
        updateDict = "123123"

        try:
            test.update(collection, updateQuery, updateDict)
        except TypeError as err:
            self.assertEquals(err.message, "Invalid Update Dict!")
        else:
            raise AssertionError

    def test_update7(self):

        test = Mongo.Mongo(config.database_host, config.database_port, True,
                           config.database_username, config.database_password)
        collection = "test"
        updateQuery = {"test1": "asdf"}
        updateDict = {"$set": {"test1": "12345"}}

        try:
            test.update(collection, updateQuery, updateDict, updateMany = 123)
        except TypeError as err:
            self.assertEquals(err.message, "Invalid Update Option!")
        else:
            raise AssertionError

    def test_update8(self):

        test = Mongo.Mongo(config.database_host, config.database_port, True,
                           config.database_username, config.database_password)
        collection = "test"
        updateQuery = {"test1": "asdf"}
        updateDict = {"$st": {"test1": "12345"}}

        try:
            test.update(collection, updateQuery, updateDict)
        except RuntimeError as err:
            self.assertEquals(err.message, "Operation Failed!")
        else:
            raise AssertionError

    def test_update9(self):

        test = Mongo.Mongo(config.database_host, config.database_port, True,
                           config.database_username, config.database_password)
        collection = "test"
        updateQuery = {"test1": "asdf"}
        updateDict = {"$st": {"test1": "12345"}}

        try:
            test.update(collection, updateQuery, updateDict, updateMany = True)
        except RuntimeError as err:
            self.assertEquals(err.message, "Operation Failed!")
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
