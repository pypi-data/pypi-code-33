import unittest

from dx_utilities.exceptions import *


class TestCodedException(unittest.TestCase):

    def test_codify(self):
        coded = codify(Exception)(1000, 'Exception')
        self.assertIsInstance(coded, Exception)

    def test_value_error(self):
        coded = CodedValueError(1000, 'Value error')
        try:
            raise coded
        except CodedValueError as e:
            self.assertEqual(coded.code, '1000')
            self.assertEqual(str(coded), 'Value error')
