from looqbox.objects.tests import ObjWebFrame
from looqbox.objects.tests import LooqObject
import unittest
import json


class TestObjectWebFrame(unittest.TestCase):
    """
    Test looq_web_frame file
    """

    def test_instance(self):
        looq_object_web_frame = ObjWebFrame("test", 200)

        self.assertIsInstance(looq_object_web_frame, LooqObject)

    def test_json_creation(self):
        # Testing JSON keys
        looq_object_web_frame = ObjWebFrame("test", 200)

        json_object = json.loads(looq_object_web_frame.to_json_structure)
        self.assertEqual(list(json_object.keys()), ["objectType", "src", "style", "enableFullscreen", "openFullscreen"],
                         msg="Failed basic JSON structure test")

        self.assertEqual(list(json_object["style"].keys()), ["width", "height"], msg="Failed style dict structure test")


if __name__ == '__main__':
    unittest.main()
