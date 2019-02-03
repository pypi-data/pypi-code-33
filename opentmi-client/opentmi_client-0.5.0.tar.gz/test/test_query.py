# pylint: disable=missing-docstring

import unittest
from opentmi_client.utils import Query, Find, Distinct


class TestRequest(unittest.TestCase):

    def test_query_empty(self):
        self.assertEqual(Query().to_string(), "{}")

    def test_query_set(self):
        self.assertEqual(Query().set("a", "b").to_string(), '{"a": "b"}')

    def test_find_empty(self):
        self.assertDictEqual(Find().params(), {"t": "find", "q": "{}"})

    def test_find_limit(self):
        self.assertDictEqual(Find().limit(1).params(), {"t": "find", "l": 1, "q": "{}"})

    def test_find_skip(self):
        self.assertDictEqual(Find().skip(1).params(), {"t": "find", "sk": 1, "q": "{}"})

    def test_find_select(self):
        self.assertDictEqual(Find().select("aa").params(), {"t": "find", "f": "aa", "q": "{}"})

    def test_find_select_multi(self):
        self.assertDictEqual(Find()
                             .select("aa")
                             .select("bb")
                             .params(),
                             {"t": "find", "f": "aa bb", "q": "{}"})

    def test_find_query(self):
        find = Find()
        find.query.set("a", "b")
        self.assertDictEqual(find.params(), {"t": "find", "q": '{"a": "b"}'})

    def test_distinct(self):
        dist = Distinct().select("a")
        self.assertDictEqual(dist.params(), {"t": "distinct", 'q': '{}', "f": "a"})


if __name__ == '__main__':
    unittest.main()