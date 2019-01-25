#!/usr/bin/python
# -*- coding:utf-8 -*-

"""
    @file:      mysql_module.py
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    @auther:    tangmi(tangmi360@gmail.com), zhouqinmin(zqm175899960@163.com)
    @date:      June 11, 2018
    @desc:      MMySQLModule
"""

import logging
import aiomysql
from aiomysql.cursors import DictCursor
from tomato.util.appmodule import AppModule
from tomato.store.mysql.mysql_batch_controller import MysqlBatchController

class MySQLModule(AppModule):

    def __init__(self, *args, **kwargs):
        super(MySQLModule, self).__init__(*args, **kwargs)
        setting = kwargs.get('setting', None)
        if setting: kwargs.update(setting)
        self._db = kwargs.get('db')
        self._host = kwargs.get('host', 'localhost')
        self._port = int(kwargs.get('port', 3306))
        self._user = kwargs.get('user')
        self._passwd = kwargs.get('passwd')
        self._minsize = int(kwargs.get('minsize', 5))
        self._maxsize = int(kwargs.get('maxsize', 5))
        self._charset = kwargs.get('charset', 'utf8')
        self._pool = None

    def setup(self):
        pass

    async def run(self):
        self._pool = await aiomysql.create_pool(host=self._host,
                                                port=self._port,
                                                user=self._user,
                                                password=self._passwd,
                                                db=self._db,
                                                minsize=self._minsize,
                                                maxsize=self._maxsize,
                                                charset=self._charset,
                                                cursorclass=DictCursor)
        async with self._pool.acquire() as conn:
            async with conn.cursor() as cur:
                await cur.execute("SELECT 1;")
                (r,) = await cur.fetchone()
                assert r == '1'
                logging.info('mysql connection success: mysql://%s:%s'
                             ';charset=%s, db[%s] '
                             'minsize[%s] maxsize[%s]',
                             self._host, self._port, self._charset,
                             self._db, self._minsize, self._maxsize)
        MysqlBatchController(self)

    async def destroy(self):
        if self._pool:
            self._pool.close()
            await self._pool.wait_closed()

    async def execute(self, sql, args):
        ret = False
        async with self._pool.acquire() as conn:
            try:
                async with conn.cursor() as cur:
                    await cur.execute(sql, args)
                    affected = cur.rowcount
                    if affected > 0:
                        ret = True
            except Exception as e:
                logging.exception(e)
                logging.exception(sql)
        return ret

    async def execute_batch(self, params):
        ret = False
        async with self._pool.acquire() as conn:
            try:
                await conn.begin()
                async with conn.cursor(aiomysql.DictCursor) as cur:
                    for p in params:
                        await cur.execute(p[0], p[1])
                    await conn.commit()
                    ret = True
            except Exception as e:
                await conn.rollback()
                logging.exception(e)
        return ret

    async def get_all(self, sql, args):
        results = None
        async with self._pool.acquire() as conn:
            try:
                async with conn.cursor() as cur:
                    await cur.execute(sql, args)
                    results = await cur.fetchall()
            except Exception as e:
                logging.exception(e)
                logging.exception(sql)
        return results

    async def get_one(self, sql, args):
        results = None
        async with self._pool.acquire() as conn:
            try:
                async with conn.cursor() as cur:
                    await cur.execute(sql, args)
                    results = await cur.fetchone()
            except Exception as e:
                logging.exception(e)
                logging.exception(sql)
        return results
