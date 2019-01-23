import unittest
from unittest.mock import MagicMock

from cone.server.ConeCore import ConeCore


class TestConeCore(unittest.TestCase):

    def setUp(self):
        self.cone_core = ConeCore()

    def test_add_task_return_an_id(self):
        id = self.cone_core.add_task({})

        self.assertIsNotNone(id)

    def test_add_task_set_id_to_given_task(self):
        task = {}
        self.cone_core.add_task(task)

        self.assertIsNotNone(task["id"])

    def test_add_two_task_return_different_ids(self):
        first_id = self.cone_core.add_task({})
        second_id = self.cone_core.add_task({})

        self.assertNotEqual(first_id, second_id)

    def test_get_next_task_return_none_when_no_task(self):
        task = self.cone_core.get_next_task()

        self.assertIsNone(task)

    def test_get_next_task_return_oldest_task(self):
        first_id = self.cone_core.add_task({})
        second_id = self.cone_core.add_task({})
        next_task = self.cone_core.get_next_task()
        second_next_task = self.cone_core.get_next_task()

        self.assertEqual(first_id, next_task["id"])
        self.assertEqual(second_id, second_next_task["id"])

    def test_get_result_return_none_when_result_not_found(self):
        id_not_found = 'id'
        result = self.cone_core.get_result(id_not_found)

        self.assertIsNone(result)

    def test_get_result_return_data_when_result_found(self):
        id = 'id'
        result_to_add = {}
        self.cone_core.add_result(id, result_to_add)
        result = self.cone_core.get_result(id)

        self.assertEqual(result, result_to_add)
