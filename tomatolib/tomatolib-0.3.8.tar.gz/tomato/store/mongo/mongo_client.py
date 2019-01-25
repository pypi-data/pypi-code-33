#!/usr/bin/python
# -*- coding:utf-8 -*-

"""
    @file:      mongo_client.py
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    @auther:    tangmi(tangmi360@gmail.com)
    @date:      June 4, 2018
    @desc:      Mongodb storage access class
"""

from motor.motor_asyncio import AsyncIOMotorClient


class MongoClient(AsyncIOMotorClient):

    def __init__(self, *args, **kwargs):
        if kwargs.get('authMechanism') == None:
            kwargs['authMechanism'] = 'SCRAM-SHA-1'
        super(MongoClient, self).__init__(*args, **kwargs)
