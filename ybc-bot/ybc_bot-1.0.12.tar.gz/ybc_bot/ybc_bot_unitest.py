import unittest
from ybc_bot import *


class MyTestCase(unittest.TestCase):
    def test_listen_ParameterTypeError(self):
        with self.assertRaisesRegex(ParameterTypeError, "^参数类型错误 : 调用listen方法时，'filename'参数类型错误。$"):
            listen(1)

    def test_listen_ParameterValueError(self):
        with self.assertRaisesRegex(ParameterValueError, "^参数数值错误 : 调用listen方法时，'filename'参数不在允许范围内。$"):
            listen('')

    def test_analysis_ParameterTypeError(self):
        with self.assertRaisesRegex(ParameterTypeError, "^参数类型错误 : 调用analysis方法时，'filename'参数类型错误。$"):
            answer_voice(1)

    def test_analysis_ParameterValueError(self):
        with self.assertRaisesRegex(ParameterValueError, "^参数数值错误 : 调用analysis方法时，'filename'参数不在允许范围内。$"):
            answer_voice('')

    def test_chat(self):
        self.assertIsNotNone(chat('你好'))

    def test_chat_ParameterTypeError(self):
        with self.assertRaisesRegex(ParameterTypeError, "^参数类型错误 : 调用chat方法时，'text'参数类型错误。$"):
            chat(1)

    def test_chat_ParameterValueError(self):
        with self.assertRaisesRegex(ParameterValueError, "^参数数值错误 : 调用chat方法时，'text'参数不在允许范围内。$"):
            chat('')


if __name__ == '__main__':
    unittest.main()
