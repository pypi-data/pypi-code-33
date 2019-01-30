"""
Unit Tests
function: String2ObjectId
"""

import unittest
import sys
from bson.objectid import ObjectId

sys.path.append("..")

from Mongo import Mongo


class TestString2ObjectId(unittest.TestCase):

    def test_String2ObjectId1(self):

        objstr = "5c4dc95cbb8b0b4811da29b4"
        objectid = ObjectId(objstr)
        test = Mongo.Mongo.String2ObjectId(objstr)
        self.assertEquals(test, objectid)

    def test_String2ObjectId2(self):

        objstr = "5c4dc95cbb8b0b4811da29b"
        try:
            Mongo.Mongo.String2ObjectId(objstr)
        except TypeError as err:
            self.assertEquals(err.message, "Invalid ObjectId!")

    def test_String2ObjectId3(self):

        objstr = 123
        try:
            Mongo.Mongo.String2ObjectId(objstr)
        except TypeError as err:
            self.assertEquals(err.message, "Invalid ObjectId!")
