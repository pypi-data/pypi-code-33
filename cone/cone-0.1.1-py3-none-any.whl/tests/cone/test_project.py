import unittest
from unittest.mock import MagicMock

from cone import project


class TestConeCore(unittest.TestCase):

    def setUp(self):
        self.keep_file_name = "keep.lua"
        self.remove_file_name = "remove.spec.lua"

    def test_filter_project_tests_remove_test_files(self):
        data = {
            self.keep_file_name: "",
            self.remove_file_name: ""
        }

        project.filter_project_tests(data)

        self.assertNotIn(self.remove_file_name, data)

    def test_filter_project_tests_keep_files(self):
        data = {
            self.keep_file_name: "",
            self.remove_file_name: ""
        }

        project.filter_project_tests(data)

        self.assertIn(self.keep_file_name, data)

    def test_filter_project_tests_remove_test_sub_files(self):
        data = {
            self.keep_file_name: {
                self.remove_file_name: ""
            }
        }

        project.filter_project_tests(data)

        self.assertIn(self.keep_file_name, data)
        self.assertNotIn(self.remove_file_name, data[self.keep_file_name])
