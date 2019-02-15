import unittest

from bigquery_schema_coerce import core

FIXTURE_PATH = "tests/fixtures/schema.json"


class TestCore(unittest.TestCase):
    def setUp(self):
        self.schema = core.parse_schema(path=FIXTURE_PATH)

    def test_coerce(self):
        candidate = {
            "name": "name1",
            "value": "123,120.02",
            "number": "2",
            "timestamp": "Feb 1 2019, 1:00",
            "series": [
                {
                    "float": "123.2",
                    "type": "type1",
                    "time": "20181129T171218Z",
                    "removal": "removed",
                }
            ],
            "single": {"float": "123.2", "type": "type1"},
        }
        result = core.coerce(candidate, self.schema)
        self.assertEqual("2019-02-01T01:00:00", result["timestamp"])
        self.assertEqual(3, len(result["series"][0]))
        self.assertNotIn("removal", result["series"][0])

    def test_convert(self):
        candidate = {
            "name": "name1",
            "value": "123,120.02",
            "number": "2",
            "timestamp": "Feb 1 2019, 1:00",
            "series": [
                {
                    "float": "123.2",
                    "type": "type1",
                    "time": "20181129T171218Z",
                    "removal": "removed",
                }
            ],
            "single": {"float": "123.2", "type": "type1"},
        }
        result = core.convert(candidate, self.schema)
        self.assertAlmostEqual(123120.02, result["value"], places=2)
        self.assertAlmostEqual(123.2, result["series"][0]["float"], places=1)
        self.assertEqual("2019-02-01T01:00:00", result["timestamp"])

    def test_project(self):
        candidate = {
            "name": "name1",
            "remove": "removeme",
            "series": [{"remove": "removeme", "type": "type1"}],
            "single": {"float": "123.2", "remove": "removeme"},
        }
        expected = {
            "name": "name1",
            "series": [{"type": "type1"}],
            "single": {"float": "123.2"},
        }
        result = core.project(candidate, self.schema)
        self.assertDictEqual(expected, result)

    def test_parse_schema(self):
        schema = list(core.parse_schema(path=FIXTURE_PATH))
        self.assertEqual(6, len(schema))
        self.assertEqual(3, len(schema[4].fields))
