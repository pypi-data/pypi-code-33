import unittest
from looqbox.objects.looq_message import ObjMessage
from looqbox.objects.looq_message import LooqObject
import json


class TestObjMessage(unittest.TestCase):
    """
    Test looq_message file
    """

    def test_instance(self):
        looq_object_message = ObjMessage("Unit Test Text")

        self.assertIsInstance(looq_object_message, LooqObject)

    def test_json_creation(self):
        # Testing JSON without pass a new style
        looq_object_message = ObjMessage("Unit Test Text")

        json_keys = list(json.loads(looq_object_message.to_json_structure).keys())

        self.assertEqual(json_keys, ["objectType", "style", "text", "type"], msg="Failed basic JSON structure test")

        # Testing JSON with other style
        looq_object_message = ObjMessage("Unit Test Text", style={"background": "red", "color": "blue"})

        json_keys = list(json.loads(looq_object_message.to_json_structure).keys())

        self.assertEqual(json_keys, ["objectType", "style", "text", "type"],
                         msg="JSON test failed with more than one style")


if __name__ == '__main__':
    unittest.main()
