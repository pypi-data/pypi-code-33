import unittest
from typing import Dict

from anji_orm import orm_register


class CouchDBTestCase(unittest.TestCase):

    def setUp(self):
        orm_register.init('couchdb://', {})

    def assertQueryEqual(self, first: Dict, second: Dict) -> None:  # pylint: disable=invalid-name
        self.assertEqual(first["url"], second["url"])
        self.assertEqual(first["method"], second["method"])
        self.assertEqual(first["json"], second["json"])
        first_context = first.get('_context', {})
        second_context = second.get('_context', {})
        for useless_key in ('table_name', 'query_identity'):
            first_context.pop(useless_key, None)
            second_context.pop(useless_key, None)
        self.assertEqual(first_context.keys(), second_context.keys())
        for key in first_context:
            if key in ('post_processors', 'pre_processors'):
                if first_context[key] is None:
                    self.assertFalse(key in second_context)
                else:
                    self.assertEqual(
                        len(first_context['post_processors']),
                        len(second_context['post_processors'])
                    )
