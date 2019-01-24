import json
import unittest

tc = unittest.TestCase("__init__")


def assert_details(details, schema, state='active'):
    print("Datamart details:\n{}".format(details))
    tc.assertIsNotNone(details)
    tc.assertEqual(details['status']['state'], state)
    tc.assertEqual(details['database_configuration']['location']['schema'], schema)