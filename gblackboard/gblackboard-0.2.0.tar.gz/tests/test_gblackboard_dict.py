#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Tests for `gblackboard` package."""

import datetime as dt
import unittest

from gblackboard import exception
from gblackboard import Blackboard
from gblackboard import SupportedMemoryType


class User(object):

    def __init__(self, name, email):
        self.name = name
        self.email = email
        self.created_at = dt.datetime.now()

    def __repr__(self):
        return '<User(name={self.name!r})>'.format(self=self)

    def __eq__(self, other):
        if self.name == other.name and self.email == other.email:
            return True
        else:
            return False


class TestGblackboard(unittest.TestCase):

    def setUp(self):
        self.blackboard = Blackboard(SupportedMemoryType.DICTIONARY)
        self.data_a = None
        self.data_b = None
        self.data_c = None

    def tearDown(self):
        self.blackboard.close()

    def callback_a(self, data):
        self.data_a = data

    def callback_b(self, data):
        self.data_b = data

    def callback_c(self, data):
        self.data_c = data

    def test_simple_data(self):
        # set first value
        first_key = 'first'
        first_value = 100
        self.blackboard.set(first_key, first_value)
        first = self.blackboard.get(first_key)
        self.assertEqual(first, first_value)
        # update first value
        first_value = 200
        self.blackboard.update(first_key, first_value)
        first = self.blackboard.get(first_key)
        self.assertEqual(first, first_value)
        # set second value (read_only)
        second_key = 'second'
        second_value = 100.1
        self.blackboard.set(second_key, second_value, read_only=True)
        second = self.blackboard.get(second_key)
        self.assertEqual(second, second_value)
        second_value = 100.2
        with self.assertRaises(exception.NotEditable):
            self.blackboard.update(second_key, second_value)
        # drop first value
        self.blackboard.drop(first_key)
        with self.assertRaises(exception.NonExistingKey):
            self.blackboard.get(first_key)
        # clear keys
        self.blackboard.clear()
        keys = self.blackboard.keys(in_list=True)
        self.assertListEqual(keys, [])
        # set third value
        third_key = 'third'
        third_value = 'hello world'
        self.blackboard.set(third_key, third_value, read_only=False)
        # test callback_a, callback_b
        self.blackboard.register_callback(third_key, self.callback_a)
        self.blackboard.register_callback(third_key, self.callback_b)
        self.blackboard.register_callback(third_key, self.callback_c)
        third_value = 'hello blackboard!'
        self.blackboard.update(third_key, third_value)
        self.assertEqual(self.data_a, third_value)
        self.assertEqual(self.data_b, third_value)
        self.assertEqual(self.data_c, third_value)
        # remove callback_a
        self.blackboard.remove_callback(third_key, self.callback_a)
        third_value = 'hello world!!'
        self.blackboard.update(third_key, third_value)
        self.assertNotEqual(self.data_a, third_value)
        self.assertEqual(self.data_b, third_value)
        self.assertEqual(self.data_c, third_value)
        # clear callbacks
        self.blackboard.clear_callbacks(third_key)
        third_value = 'clear callbacks'
        self.blackboard.update(third_key, third_value)
        self.assertNotEqual(self.data_a, third_value)
        self.assertNotEqual(self.data_b, third_value)
        self.assertNotEqual(self.data_c, third_value)

    def test_complex_data(self):
        # user1 data
        user1_key = 'user1'
        user1_val = User("G.Ted", "gted221@gmail.com")
        self.blackboard.set(user1_key, user1_val)
        user1_val = self.blackboard.get(user1_key)
        self.assertEqual(type(user1_val), User)
        self.assertEqual(repr(user1_val), "<User(name='G.Ted')>")
        # user2 data
        user2_key = 'user2'
        user2_val = User("Foo", "foo@bar.com")
        self.blackboard.set(user2_key, user2_val)
        self.blackboard.register_callback(user2_key, self.callback_a)
        user2_val = self.blackboard.get(user2_key)
        user2_val.name = 'Bar'
        self.blackboard.update(user2_key, user2_val)
        user2_val = self.blackboard.get(user2_key)
        self.assertEqual(type(user2_val), User)
        self.assertEqual(repr(user2_val), "<User(name='Bar')>")
        self.assertEqual(type(self.data_a), User)
        self.assertEqual(repr(self.data_a), "<User(name='Bar')>")
        # user list
        user_list_key = 'users'
        user_list_val = [user1_val, user2_val]
        self.blackboard.set(user_list_key, user_list_val)
        user_list_val = self.blackboard.get(user_list_key)
        self.assertEqual(user_list_val[0], user1_val)
        self.assertListEqual(user_list_val, [user1_val, user2_val])


if __name__ == '__main__':
    unittest.main()
