import unittest
import os
from ybc_wordcloud import *
from ybc_exception import *


class TestYbcWordcloud(unittest.TestCase):
    path_pic = os.path.join(os.path.split(os.path.abspath(__file__))[0], 'test.jpg')

    def test_cut(self):
        self.assertIsNotNone(cut("你好你好"))

    def test_cut2str(self):
        self.assertIsNotNone(cut2str("你好你好大家好"))

    def test_wordcloud(self):
        self.assertIsNotNone(wordcloud(cut("你好你好大家好，我的名字叫艾连叶卡"), bgfile=TestYbcWordcloud.path_pic))

    def test_cut_exType(self):
        with self.assertRaisesRegex(ParameterTypeError, "^参数类型错误 : 调用cut方法时，'text'参数类型错误。$"):
            cut(123)

    def test_cut_exValue(self):
        with self.assertRaisesRegex(ParameterValueError, "^参数数值错误 : 调用cut方法时，'text'参数不在允许范围内。$"):
            cut('')

    def test_cut2str_exType(self):
        with self.assertRaisesRegex(ParameterTypeError, "^参数类型错误 : 调用cut2str方法时，'text'参数类型错误。$"):
            cut2str(123)

    def test_cut2str_exValue(self):
        with self.assertRaisesRegex(ParameterValueError, "^参数数值错误 : 调用cut2str方法时，'text'参数不在允许范围内。$"):
            cut2str('')

    def test_wordcloud_exType(self):
        with self.assertRaisesRegex(ParameterTypeError, "^参数类型错误 : 调用wordcloud方法时，'text'、'bgfile'参数类型错误。$"):
            wordcloud(1, 1)

    def test_wordcloud_exValue(self):
        with self.assertRaisesRegex(ParameterValueError, "^参数数值错误 : 调用wordcloud方法时，'text'、'bgfile'参数不在允许范围内。$"):
            wordcloud('', '')


if __name__ == '__main__':
    unittest.main()
