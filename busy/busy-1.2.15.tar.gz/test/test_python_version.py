from unittest import TestCase
import sys

import busy

class TestPythonVersion(TestCase):

    def test_python_version(self):
        self.assertTrue(sys.version_info >= busy.PYTHON_VERSION)
