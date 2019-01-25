#!/usr/bin/python
# -*- coding:utf-8 -*-

"""
    @file:      mongo_helper.py
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    @auther:    tangmi(tangmi360@gmail.com)
    @date:      September 04, 2018
    @desc:      Mongo Helper
"""

from bson.objectid import ObjectId


class MongoHelper(object):

    def __init__(self, *args, **kwargs):
        self.key_map = {}
        self._coll = args[0]

    def mapping(self, item, result=None):
        if result == None:
            result = {}
        for k, v in item.items():
            k = self.key_map.get(k, k)
            if isinstance(v, dict):
                result[k] = {}
                mapping(v, result[k])
            else:
                result[k] = v
        return result

    def __getattr__(self, attr):
        return getattr(self._coll, attr)

    async def find_by_id(self, _id):
        doc = await self._coll.find_one({'_id': ObjectId(_id)})
        return doc
