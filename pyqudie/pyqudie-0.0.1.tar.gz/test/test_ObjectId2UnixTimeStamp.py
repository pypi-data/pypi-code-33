'''
Unit Tests
function: ObjectId2UnixTimeStamp
'''

import unittest
import sys
from bson.objectid import ObjectId
import time

sys.path.append("..")

from pyqudie import Mongo


class TestObjectId2UnixTimeStamp(unittest.TestCase):

    def test_ObjectId2UnixTimeStamp1(self):

        objstr = "5c4dc95cbb8b0b4811da29b4"
        test = Mongo.Mongo.ObjectId2UnixTimeStamp(objstr)
        objectid = ObjectId(objstr)
        self.assertEquals(test, time.mktime(objectid.generation_time.timetuple()))

    def test_ObjectId2UnixTimeStamp2(self):

        objstr = "5c4dc95cbb8b0b4811da29b4"
        objectid = ObjectId(objstr)
        test = Mongo.Mongo.ObjectId2UnixTimeStamp(objectid)
        self.assertEquals(test, time.mktime(objectid.generation_time.timetuple()))

    def test_ObjectId2UnixTimeStamp3(self):

        objstr = "5c4dc95cbb8b0b4811da29b"
        try:
            Mongo.Mongo.ObjectId2UnixTimeStamp(objstr)
        except TypeError as err:
            self.assertEquals(err.message, "Invalid ObjectId!")

    def test_ObjectId2UnixTimeStamp4(self):

        objstr = 123
        try:
            Mongo.Mongo.ObjectId2UnixTimeStamp(objstr)
        except TypeError as err:
            self.assertEquals(err.message, "Invalid ObjectId!")
