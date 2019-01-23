#!/usr/bin/python
# -*- coding:utf-8 -*-

import asyncio
import unittest

from tomato.util import Log
from tomato.transport import HttpClient
from tomato.transport import HttpServer


class TestHttpClient(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.log = Log(filename='unit_test.log', cmdlevel='INFO')
        cls.loop = asyncio.new_event_loop()
        asyncio.set_event_loop(cls.loop)
        cls.http_server = HttpServer(host='localhost', port=8888)
        cls.loop.run_until_complete(cls.http_server.run())
        cls.http_client = HttpClient()

    @classmethod
    def tearDownClass(cls):
        cls.loop.run_until_complete(cls.http_client.close())
        cls.loop.run_until_complete(cls.http_server.close())
        cls.loop.run_until_complete(asyncio.sleep(0.250))
        cls.loop.stop()
        cls.loop.close()

    def setUp(self):
        self.url = 'http://localhost:8888'

    def tearDown(self):
        pass

    def test_http_status(self):
        self.log.info('test_http_status')
        async def http_status():
            http_get = self.http_client.get(self.url)
            response = await http_get
            return response.status

        status = self.loop.run_until_complete(http_status())
        self.assertEqual(status, 200)
