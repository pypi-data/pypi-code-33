import unittest

from bigquery_schema_coerce import core

FIXTURE_PATH = "tests/fixtures/schema.json"


class TestCore(unittest.TestCase):
    def test_convert_fields(self):
        candidate = {
            "name": "name1",
            "value": "123,120.02",
            "number": "2",
            "timestamp": "Feb 1 2019, 1:00",
            "series": [{"float": "123.2", "type": "type1", "time": "20181129T171218Z"}],
            "single": {"float": "123.2", "type": "type1"},
        }
        schema = core.parse_schema(path=FIXTURE_PATH)
        result = core.convert_fields(candidate, schema)
        self.assertAlmostEqual(123120.02, result["value"], places=2)
        self.assertAlmostEqual(123.2, result["series"][0]["float"], places=1)
        self.assertEqual("2019-02-01T01:00:00", result["timestamp"])

    def test_parse_schema(self):
        schema = list(core.parse_schema(path=FIXTURE_PATH))
        self.assertEqual(6, len(schema))
        self.assertEqual(3, len(schema[4].fields))
