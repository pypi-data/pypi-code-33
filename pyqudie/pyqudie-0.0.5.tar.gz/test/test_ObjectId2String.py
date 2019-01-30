"""
Unit Tests
function: ObjectId2String
"""

import unittest
import sys
from bson.objectid import ObjectId

sys.path.append("..")

from pyqudie import Mongo
from pyqudie.MongoExceptions import *


class TestObjectId2String(unittest.TestCase):

    def test_ObjectId2String1(self):

        objstr = "5c4dc95cbb8b0b4811da29b4"
        objectid = ObjectId(objstr)
        test = Mongo.Mongo.ObjectId2String(objectid)
        self.assertEquals(test, objstr)

    def test_ObjectId2String2(self):

        objstr = "5c4dc95cbb8b0b4811da29b"
        try:
            Mongo.Mongo.ObjectId2String(objstr)
        except InvalidObjectIdException as err:
            self.assertEquals(err.message, "Invalid ObjectId!")
