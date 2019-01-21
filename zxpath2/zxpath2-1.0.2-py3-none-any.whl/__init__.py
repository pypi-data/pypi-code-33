# -*- coding: utf-8 -*-
"""
-------------------------------------------------
   File Name：    __init__.py.py
   Author :       Zhang Fan
   date：         2018/11/3
   Description :
-------------------------------------------------
"""
__author__ = 'Zhang Fan'

from . import _base_library
from ._Text_Element import _Text_Element
from ._Element_List import _Element_List
from ._Element import _Element


def load(src):
    if _base_library.is_element(src):
        assert not src is None, 'etree对象为None'
    else:
        assert isinstance(src, str), '只能传入etree对象或一个html结构的str类型, 你传入的是{}'.format(type(src))
        assert src, '不能传入空字符串'
        src = _base_library.to_etree(src)
    return _Element(src)
