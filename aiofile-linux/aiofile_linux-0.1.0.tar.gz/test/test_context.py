# coding: UTF-8

import asyncio
import os
import unittest

from aiofile_linux import AIOContext, ReadCmd


class MyTestCase(unittest.TestCase):
    _CONTENTS = 'content\n'
    _TEST_FILE_NAME = 'test.txt'

    def tearDown(self) -> None:
        super().tearDown()
        os.remove('test.txt')

    def setUp(self) -> None:
        super().setUp()
        with open(self._TEST_FILE_NAME, 'w') as fp:
            fp.write(self._CONTENTS)

    def test_with(self):
        async def _inner():
            with AIOContext(1) as ctx, open(self._TEST_FILE_NAME) as fp:
                buffer = bytearray(64)
                cmd = ReadCmd(fp, buffer)

                ret = await ctx.submit(cmd)

                self.assertEqual(1, len(ret))
                self.assertEqual(self._CONTENTS, ret[0].stripped_buffer().decode())

        asyncio.run(_inner())
