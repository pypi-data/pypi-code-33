# -*- coding: utf-8 -*-


class CollectionUtil:
    '''集合工具类'''

    @staticmethod
    def tuple_to_list(t):
        '''
        元组 转 列表
        :param t: a touple
        :return: a list
        '''
        return [x for x in t]

    @staticmethod
    def merge_dicts(*dict_args):
        '''
        字典合并
        :param dict_args: 多个字典
        :return: 合并后的字典
        '''
        result = {}
        for dictionary in dict_args:
            result.update(dictionary)
        return result
