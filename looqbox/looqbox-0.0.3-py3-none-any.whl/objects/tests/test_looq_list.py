from looqbox.objects.tests import ObjList
from looqbox.objects.tests import LooqObject
import unittest
import json

class TestObjectList(unittest.TestCase):
    """
    Test looq_list file
    """

    def test_instance(self):
        looq_object_list = ObjList("test", "test fake")

        self.assertIsInstance(looq_object_list, LooqObject)

    def test_json_creation(self):
        # Testing JSON keys
        looq_object_list = ObjList("test", "test fake")

        json_keys = list(json.loads(looq_object_list.to_json_structure).keys())
        self.assertEqual(json_keys, ["objectType", "title", "list"],
                         msg="Failed basic JSON structure test")


if __name__ == '__main__':
    unittest.main()
