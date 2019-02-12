import unittest
from ybc_browser import *


class MyTestCase(unittest.TestCase):
    def test_browser(self):
        self.assertIsNotNone(open_browser("猿辅导"))

    def test_open_browser(self):
        self.assertEqual(-1, open_browser("1234567"))

    def test_open_local_page(self):
        self.assertIsNotNone(open_local_page("ybc_browser.py"))

    def test_browser_ParameterTypeError(self):
        with self.assertRaisesRegex(ParameterTypeError, "^参数类型错误 : 调用open_browser方法时，'text'参数类型错误。$"):
            open_browser(1)

    def test_browser_ParameterValueError(self):
        with self.assertRaisesRegex(ParameterValueError, "^参数数值错误 : 调用open_browser方法时，'text'参数不在允许范围内。$"):
            open_browser('')

    def test_page_ParameterTypeError(self):
        with self.assertRaisesRegex(ParameterTypeError, "^参数类型错误 : 调用open_local_page方法时，'file_name'参数类型错误。$"):
            open_local_page(1)

    def test_page_ParameterValueError(self):
        with self.assertRaisesRegex(ParameterValueError, "^参数数值错误 : 调用open_local_page方法时，'file_name'参数不在允许范围内。$"):
            open_local_page('')


if __name__ == '__main__':
    unittest.main()
