import unittest
from ybc_idcard_ocr import *


class MyTestCase(unittest.TestCase):
    def test_idcard_info(self):
        res = {'name': '二哈', 'sex': '男', 'nation': '汉', 'birth': '2015/3/8', 'address': '河南省安阳市文峰区', 'id': '410502201503081234', 'card_type': 0, 'recognize_warn_code': [], 'recognize_warn_msg': []}
        self.assertEqual(res, idcard_info('test.jpg'))

    def test_idcard_info_error(self):
        self.assertEqual(-1, idcard_info('cup.jpg'))

    def test_idcard_info_typeError(self):
        with self.assertRaisesRegex(ParameterTypeError, "^参数类型错误 : 调用idcard_info方法时，'filename'参数类型错误。$"):
            idcard_info(123)

    def test_idcard_infor_valueError(self):
        with self.assertRaisesRegex(ParameterValueError, "^参数数值错误 : 调用idcard_info方法时，'filename'参数不在允许范围内。$"):
            idcard_info('')


if __name__ == '__main__':
    unittest.main()
