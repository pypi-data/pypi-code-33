import asyncio
from enum import Enum

import asynctest

from anji_orm import ensure_element


class NotPrettyEnum(Enum):

    first = 'first'
    second = 'second'
    haha = 'haha'


class EnsureElementTest(asynctest.TestCase):

    def setUp(self):
        self.value = '5'
        self.value_list = ['5', 6, 75]
        self.value_dict = {
            't1': ['t5', 't7'],
            't2': 5,
            6: '57'
        }

    async def gen_value(self):
        return self.value

    async def gen_value_list(self):
        return self.value_list

    async def gen_value_dict(self):
        return self.value_dict

    def gen_value_list_of_dicts(self, loop):
        return [
            loop.create_task(self.gen_value_dict()),
            loop.create_task(self.gen_value_dict()),
            self.value_dict,
            self.value
        ]

    def gen_value_dict_with_lists(self, loop):
        return {
            1: loop.create_task(self.gen_value_list()),
            2: loop.create_task(self.gen_value_list()),
            3: self.value_list,
            4: self.value
        }

    def get_value_dict_with_dicts(self, loop):
        return {
            1: loop.create_task(self.gen_value_list()),
            2: loop.create_task(self.gen_value_dict()),
            3: self.value_list,
            4: self.value
        }

    async def test_simple_no_await(self):
        self.assertEqual(self.value, await ensure_element(self.value))

    async def test_simple_no_await_list(self):
        self.assertEqual(self.value_list, await ensure_element(self.value_list))

    async def test_simple_no_await_dict(self):
        self.assertEqual(self.value_dict, await ensure_element(self.value_dict))

    async def test_simple_await(self):
        loop = asyncio.get_event_loop()
        self.assertEqual(self.value, await ensure_element(loop.create_task(self.gen_value())))

    async def test_simple_list(self):
        loop = asyncio.get_event_loop()
        self.assertEqual(self.value_list, await ensure_element(loop.create_task(self.gen_value_list())))

    async def test_simple_dict(self):
        loop = asyncio.get_event_loop()
        self.assertEqual(self.value_dict, await ensure_element(loop.create_task(self.gen_value_dict())))

    async def test_dict_in_list(self):
        loop = asyncio.get_event_loop()
        self.assertEqual(
            [self.value_dict, self.value_dict, self.value_dict, self.value],
            await ensure_element(self.gen_value_list_of_dicts(loop))
        )

    async def test_list_in_dict(self):
        loop = asyncio.get_event_loop()
        self.assertEqual(
            {1: self.value_list, 2: self.value_list, 3: self.value_list, 4: self.value},
            await ensure_element(self.gen_value_dict_with_lists(loop))
        )

    async def test_dict_in_dict(self):
        loop = asyncio.get_event_loop()
        self.assertEqual(
            {1: self.value_list, 2: self.value_dict, 3: self.value_list, 4: self.value},
            await ensure_element(self.get_value_dict_with_dicts(loop))
        )
