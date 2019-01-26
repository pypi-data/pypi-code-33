from txplib.library.nlp_library import NLPLibrary
import unittest
import os
import json


class NLPLibraryTests(unittest.TestCase):

    def setUp(self):
        self.k = NLPLibrary()

        self.k.add_search_path([os.path.join(os.path.abspath(__file__).replace("nlp_library_tests.py", ""), "resources"),])
        self.k.update_catalog()

    def test_set_type(self):

        self.k.load_content('test_set')

        self.assertIn("a", self.k.get("test_set"))
        self.assertIn("b", self.k.get("test_set"))

        # test customization
        self.k.drop('test_set', {"a", })
        self.k.add('test_set', ['d', ])

        self.assertNotIn("a", self.k.get("test_set"))
        self.assertIn('d', self.k.get("test_set"))

    def test_function_type(self):
        self.k.load_content('test_func', 'nlp_library_test')

        test_fun = self.k.get('test_func')
        pos_tagged_result = test_fun("")

        self.assertTrue(pos_tagged_result)

    def test_dict_type(self):
        # test dict type
        self.k.load_content('test_dict')
        self.assertEqual(0, self.k.get("test_dict")["a"])

        # test customization
        self.k.add('test_dict', {'d': 3})
        self.k.drop('test_dict', {"a",})
        self.assertEqual(
            self.k.get('test_dict')["d"],
            3
        )

        self.assertNotIn("a", self.k.get('test_dict'))
        self.k.show_items()


class MockedNLPLibrary(NLPLibrary):

    def __init__(self, class_name_to_mocked_resource_dict):
        self.class_name_to_mocked_resource_dict = class_name_to_mocked_resource_dict

    def get(self, class_name):
        if class_name in self.class_name_to_mocked_resource_dict:
            return self.class_name_to_mocked_resource_dict[class_name]

        return None

    def load_content(self, class_name, library_name=None):
        return True

    def is_loaded(self, class_name):
        return True


def load_resources_json(file_name):
    with open(os.path.join(os.path.abspath(__file__).replace("nlp_library_tests.py", ""), "resources/" + file_name), "r") as fp:
        return json.load(fp)


def dump_resources_json(file_name, obj):
    with open(os.path.join(os.path.abspath(__file__).replace("nlp_library_tests.py", ""), "resources/" + file_name), "w") as fp:
        return json.dump(obj, fp)


