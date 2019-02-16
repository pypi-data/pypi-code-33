# -*- coding: utf-8 -*-

"""Tests for `gblackboard` package."""

import unittest
import os

from gblackboard import exception
from gblackboard.wrapper import RedisWrapper, DictionaryWrapper
from gblackboard import Blackboard, SupportedMemoryType

from gblackboard import wrapper
wrapper.DEV_MODE = True


FILE_PATH = './gblackboard.pickle'


class Address:

    def __init__(self, country, city):
        self.country = country
        self.city = city

    def __repr__(self):
        return "{} / {}".format(self.city, self.country)

    def __eq__(self, other):
        return self.country == other.country and self.city == other.city


class User:

    def __init__(self, name, skills, age, address):
        self.name = name
        self.skills = skills
        self.age = age
        self.address = address

    def __repr__(self):
        rstr = "[{}]\n".format(self.name)
        rstr += "* Skills: {}\n".format(self.skills)
        rstr += "* Age: {}\n".format(self.age)
        rstr += "* Address: {}".format(self.address)
        return rstr

    def __eq__(self, other):
        name_eq = (self.name == other.name)
        skills_eq = True
        for skill in self.skills:
            skills_eq = skills_eq and (skill in other.skills)
        skills_eq = skills_eq and (len(self.skills) == len(other.skills))
        age_eq = (self.age == other.age)
        address_eq = (self.address == other.address)
        return name_eq and skills_eq and age_eq and address_eq


class TestSaveLoad(unittest.TestCase):
    """Tests for `gblackboard` package."""

    def setUp(self):
        self.data = None

    def tearDown(self):
        pass

    def __make_dummy_data(self, wrapper):
        self.data = {
            'hello': 'world',
            'name': 'G.Ted',
            'skills': ['Python (2 & 3)', 'Git', 'Docker', 'ROS'],
            'age': 20.5,
            'address': {
                'country': 'S. Korea',
                'city': 'Seoul'
            },
            'user_info': User(
                name='G.Ted',
                skills=['Python (2 & 3)', 'Git', 'Docker', 'ROS'],
                age=20.5,
                address=Address(
                    country='S. Korea',
                    city='Seoul'
                )
            )
        }
        for k, v in self.data.items():
            wrapper.set(k, v)

    def test_dict_wrapper(self):
        wrapper = DictionaryWrapper()
        self.__make_dummy_data(wrapper)
        wrapper.save(FILE_PATH)
        wrapper.close()
        # create new wrapper
        wrapper = DictionaryWrapper()
        wrapper.load(FILE_PATH)
        self.assertEqual(wrapper.get('hello'), self.data['hello'])
        self.assertEqual(wrapper.get('name'), self.data['name'])
        self.assertListEqual(wrapper.get('skills'), self.data['skills'])
        self.assertEqual(wrapper.get('age'), self.data['age'])
        self.assertDictEqual(wrapper.get('address'), self.data['address'])
        self.assertEqual(wrapper.get('user_info'), self.data['user_info'])
        other_user = User(
            name='Druru',
            skills=['C++ 11', 'Git', 'Docker', 'Unreal Engine'],
            age=27.9,
            address=Address(
                country='S. Korea',
                city='Incheon'
            )
        )
        self.assertNotEqual(wrapper.get('user_info'), other_user)
        wrapper.close()

    def test_redis_wrapper(self):
        wrapper = RedisWrapper(host='localhost', flush=True)
        self.__make_dummy_data(wrapper)
        wrapper.save(FILE_PATH)
        wrapper.close()
        # create new wrapper
        wrapper = RedisWrapper(host='localhost', flush=True)
        wrapper.load(FILE_PATH)
        self.assertEqual(wrapper.get('hello'), self.data['hello'])
        self.assertEqual(wrapper.get('name'), self.data['name'])
        self.assertListEqual(wrapper.get('skills'), self.data['skills'])
        self.assertEqual(wrapper.get('age'), self.data['age'])
        self.assertDictEqual(wrapper.get('address'), self.data['address'])
        self.assertEqual(wrapper.get('user_info'), self.data['user_info'])
        other_user = User(
            name='Druru',
            skills=['C++ 11', 'Git', 'Docker', 'Unreal Engine'],
            age=27.9,
            address=Address(
                country='S. Korea',
                city='Incheon'
            )
        )
        self.assertNotEqual(wrapper.get('user_info'), other_user)
        wrapper.close()

    def test_redis_save_dict_read(self):
        wrapper = RedisWrapper(host='localhost', flush=True)
        self.__make_dummy_data(wrapper)
        wrapper.save(FILE_PATH)
        wrapper.close()
        # create new wrapper
        wrapper = DictionaryWrapper()
        wrapper.load(FILE_PATH)
        self.assertEqual(wrapper.get('hello'), self.data['hello'])
        self.assertEqual(wrapper.get('name'), self.data['name'])
        self.assertListEqual(wrapper.get('skills'), self.data['skills'])
        self.assertEqual(wrapper.get('age'), self.data['age'])
        self.assertDictEqual(wrapper.get('address'), self.data['address'])
        self.assertEqual(wrapper.get('user_info'), self.data['user_info'])
        other_user = User(
            name='Druru',
            skills=['C++ 11', 'Git', 'Docker', 'Unreal Engine'],
            age=27.9,
            address=Address(
                country='S. Korea',
                city='Incheon'
            )
        )
        self.assertNotEqual(wrapper.get('user_info'), other_user)
        wrapper.close()

    def test_dict_save_redis_read(self):
        wrapper = DictionaryWrapper()
        self.__make_dummy_data(wrapper)
        wrapper.save(FILE_PATH)
        wrapper.close()
        # create new wrapper
        wrapper = RedisWrapper(host='localhost', flush=True)
        wrapper.load(FILE_PATH)
        self.assertEqual(wrapper.get('hello'), self.data['hello'])
        self.assertEqual(wrapper.get('name'), self.data['name'])
        self.assertListEqual(wrapper.get('skills'), self.data['skills'])
        self.assertEqual(wrapper.get('age'), self.data['age'])
        self.assertDictEqual(wrapper.get('address'), self.data['address'])
        self.assertEqual(wrapper.get('user_info'), self.data['user_info'])
        other_user = User(
            name='Druru',
            skills=['C++ 11', 'Git', 'Docker', 'Unreal Engine'],
            age=27.9,
            address=Address(
                country='S. Korea',
                city='Incheon'
            )
        )
        self.assertNotEqual(wrapper.get('user_info'), other_user)
        wrapper.close()

    def test_save_load_on_blackboard(self):
        blackboard = Blackboard(SupportedMemoryType.DICTIONARY)
        blackboard.set('hello', 'world', read_only=True)
        blackboard.save()
        blackboard.close()
        blackboard = Blackboard(SupportedMemoryType.DICTIONARY)
        blackboard.load()
        self.assertEqual(blackboard.get('hello'), 'world')
        with self.assertRaises(exception.NotEditable):
            blackboard.update('hello', 'G.Ted')
        with self.assertRaises(exception.UnsafeLoading):
            blackboard.load()
        druru = User(
            name='Druru',
            skills=['C++ 11', 'Git', 'Docker', 'Unreal Engine'],
            age=27.9,
            address=Address(
                country='S. Korea',
                city='Incheon'
            )
        )
        blackboard.set('user', druru, read_only=False)
        gted = User(
            name='G.Ted',
            skills=['Python (2 & 3)', 'Git', 'Docker', 'ROS'],
            age=20.5,
            address=Address(
                country='S. Korea',
                city='Seoul'
            )
        )
        blackboard.update('user', gted)
        blackboard.save()
        blackboard.close()
        blackboard = Blackboard(SupportedMemoryType.REDIS)
        blackboard.load()
        self.assertEqual(blackboard.get('hello'), 'world')
        self.assertEqual(blackboard.get('user'), gted)
        blackboard.close()
        # remove saved gblackboard directory and files
        gblackboard_path = './.gblackboard'
        if os.path.exists(gblackboard_path):
            for root, dirs, files in os.walk(gblackboard_path, topdown=False):
                for name in files:
                    os.remove(os.path.join(root, name))
                for name in dirs:
                    os.rmdir(os.path.join(root, name))
                os.rmdir(root)


if __name__ == '__main__':
    unittest.main()
