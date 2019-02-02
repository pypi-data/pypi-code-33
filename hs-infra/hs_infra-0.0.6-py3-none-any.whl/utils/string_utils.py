import re
from datetime import datetime


class StringUtils:

    @classmethod
    def convert_to_string(cls, obj, default=""):
        if obj is None:
            return default
        if type(obj) is str:
            pass
        if type(obj) is bytearray:
            obj = obj.decode("utf8")
        if type(obj) is bytes:
            obj = obj.decode("utf8")
        if type(obj) is int:
            obj = str(obj)
        if type(obj) is float:
            obj = str(obj)
        if type(obj) is dict:
            obj = str(obj)
        if type(obj) is bool:
            obj = str(obj)
        if isinstance(obj, datetime):
            obj = str(obj)

        return obj

    @classmethod
    def remove_special_characters(cls, string):
        return re.sub('[\n|\t|\r]', '', string)

    @classmethod
    def convert_arabic_to_persian(cls, obj):
        if isinstance(obj, str):
            obj = obj.replace('\u064a', '\u06cc')
            # obj = obj.replace('ي', 'ی')
            obj = obj.replace('\u0649', '\u06cc')
            # obj = obj.replace('ى', 'ی')
            obj = obj.replace('\u0643', '\u06a9')
            # obj = obj.replace('ك', 'ک')
            obj = obj.replace('\u0664', '\u06f4')
            # obj = obj.replace('٤', '۴')
            obj = obj.replace('\u0665', '\u06f5')
            # obj = obj.replace('٥', '۵')
            obj = obj.replace('\u0666', '\u06f6')
            # obj = obj.replace('٦', '۶')
            obj = obj.replace('\u00ac', '\u200c')  # pseudo space
        return obj

    @classmethod
    def digit_to_ar(cls, obj):
        if isinstance(obj, str):
            table = {
                48: 1632,  # 0
                49: 1633,  # 1
                50: 1634,  # 2
                51: 1635,  # 3
                52: 1636,  # 4
                53: 1637,  # 5
                54: 1638,  # 6
                55: 1639,  # 7
                56: 1640,  # 8
                57: 1641,  # 9

                1776: 1632,  # 0
                1777: 1633,  # 1
                1778: 1634,  # 2
                1779: 1635,  # 3
                1780: 1636,  # 4
                1781: 1637,  # 5
                1782: 1638,  # 6
                1783: 1639,  # 7
                1784: 1640,  # 8
                1785: 1641,  # 9
            }
            obj = obj.translate(table)
        return obj

    @classmethod
    def digit_to_fa(cls, obj):
        if isinstance(obj, str):
            table = {
                48: 1776,  # 0
                49: 1777,  # 1
                50: 1778,  # 2
                51: 1779,  # 3
                52: 1780,  # 4
                53: 1781,  # 5
                54: 1782,  # 6
                55: 1783,  # 7
                56: 1784,  # 8
                57: 1785,  # 9

                1632: 1776,  # 0
                1633: 1777,  # 1
                1634: 1778,  # 2
                1635: 1779,  # 3
                1636: 1780,  # 4
                1637: 1781,  # 5
                1638: 1782,  # 6
                1639: 1783,  # 7
                1640: 1784,  # 8
                1641: 1785,  # 9

            }
            obj = obj.translate(table)
        return obj

    @classmethod
    def digit_to_en(cls, obj):
        if isinstance(obj, str):
            table = {
                1632: 48,  # 0
                1633: 49,  # 1
                1634: 50,  # 2
                1635: 51,  # 3
                1636: 52,  # 4
                1637: 53,  # 5
                1638: 54,  # 6
                1639: 55,  # 7
                1640: 56,  # 8
                1641: 57,  # 9

                1776: 48,  # 0
                1777: 49,  # 1
                1778: 50,  # 2
                1779: 51,  # 3
                1780: 52,  # 4
                1781: 53,  # 5
                1782: 54,  # 6
                1783: 55,  # 7
                1784: 56,  # 8
                1785: 57,  # 9
            }
            obj = obj.translate(table)
        return obj
