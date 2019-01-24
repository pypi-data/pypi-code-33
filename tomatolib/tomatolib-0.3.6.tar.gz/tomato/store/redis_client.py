#!/usr/bin/python
# -*- coding:utf-8 -*-

"""
    @file:      redis_client.py
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    @auther:    tangmi(tangmi360@gmail.com)
    @date:      June 11, 2018
    @desc:      Redis storage access class
"""

import aioredis


class RedisClient(aioredis.ConnectionsPool):

    def __init__(self, *args, **kwargs):
        super(RedisClient, self).__init__(*args, **kwargs)

    async def close(self):
        super().close()
        await self.wait_closed()
