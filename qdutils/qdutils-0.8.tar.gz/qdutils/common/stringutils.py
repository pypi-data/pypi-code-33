#  -*- coding: utf-8 -*-

'''

@desc: 
@author: tony
@Date: 2018/12/27 上午10:37

'''

import hashlib


class stringutils(object):
    @staticmethod
    def is_empty(val):
        result = True
        if val and str(val).strip():
            result = False
        return result

    @staticmethod
    def not_empty(val):
        return not stringutils.is_empty(val)

    @staticmethod
    def md5(val):
        m2 = hashlib.md5()
        m2.update(val)
        return m2.hexdigest()
