#!/usr/bin/python
# -*- coding:utf-8 -*-

"""
    @file:      sql_param_collections.py
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    @auther:    zhouqinmin(zqm175899960@163.com)
    @date:      January 23, 2019
    @desc:      SqlParamCollections
"""

# normal_param_list : normal sql param, eg: A = 1
# normal_linker_op_list : link op symbol, link normal sql param, eg: and or
# group_by_param_list : group by param, eg: A
# having_param_list : having parmam, eg: having sum(A) > 100
# order_by_param_list : order by params eg: order by A asc
# limit_param : limit param eg: limit 1, 10
import functools
from collections import namedtuple


NormalSqlParam = namedtuple('NormalSqlParam', ['key', 'operator', 'value', 'is_normal']) #A = 10#A in (1, 2, 3)#A between 1 and 2
LimitSqlParam = namedtuple('LimitSqlParam', ['offset', 'rows']) #limit 0, 10
GroupBySqlParam = namedtuple('GroupBySqlParams', ['key']) #group by A
OrderBySqlParam = namedtuple('OrderBySqlParam', ['key', 'order_dsc']) #order by A asc
HavingSqlParam = namedtuple('HavingSqlParam', ['key', 'operator', 'value']) 
SelectClauseParam = namedtuple('SelectClauseParam', ['sql', 'params'])

class SqlParamCollections(object):
    def __init__(self, 
            normal_param_list=[], 
            normal_linker_op_list = [], 
            group_by_param_list=[],
            having_param_list = [], 
            having_linker_op = [],
            order_by_param_list=[],
            limit_param=None
            ):
        self.__data = dict()
        self.__data['normal_param'] = list()
        self.__data['linker_op_list'] = list()
        self.__data['limit'] = list()
        self.__data['order_by'] = list()
        self.__data['group_by'] = list()
        self.__data['having'] = list()
        self.__data['having_linker_op_list'] = list()
        if normal_param_list and len(normal_param_list) != 0:
            self.extend_normal_param(normal_param_list)
        if order_by_param_list and len(order_by_param_list) != 0:
            self.__data['order_by'].extend(order_by_param_list)
        if group_by_param_list and len(group_by_param_list) != 0:
            self.__data['group_by'].extend(group_by_param_list)
        if normal_linker_op_list and len(normal_linker_op_list) != 0:
            self.__data['linker_op_list'].extend(normal_linker_op_list)
        if having_param_list and len(having_param_list) != 0:
            self.__data['having'].extend(having_param_list)
        if having_linker_op and len(having_linker_op) != 0:
            self.__data['having_linker_op_list'].extend(having_linker_op)
        if limit_param is not None:
            self.__data['limit'].append(limit_param)

        self.make_functions = {
            'normal_param':functools.partial(SqlParamCollections.make_where_sql_clause, params_data=self.__data['normal_param'], linker_op_data=self.__data['linker_op_list']),
            'group_by':functools.partial(SqlParamCollections.make_groupby_sql_clause, data=self.__data['group_by']),
            'order_by':functools.partial(SqlParamCollections.make_orderby_sql_clause, data=self.__data['order_by']),
            'limit':functools.partial(SqlParamCollections.make_limit_sql_clause, data=self.__data['limit']),
            'having':functools.partial(SqlParamCollections.make_having_sql_clause, params_data=self.__data['having'], linker_op_data=self.__data['having_linker_op_list'])
        }

    @property
    def data(self):
        return self.__data

    @data.setter
    def data(self, value):
        self.__data = value

    def add_normal_param(self, normal_param):
        self.__data['normal_param'].append(normal_param)
        return len(self.__data)

    def extend_normal_param(self, normal_param_list):
        self.__data['normal_param'].extend(normal_param_list)

    def add_group_by_param(self, group_by_param):
        self.__data['group_by'].append(group_by_param)

    def add_order_by_param(self, order_by_param):
        self.__data['order_by'].append(order_by_param)

    def add_having_param(self, having_param):
        self.__data['having'].append(having_param)

    def extend_having_param(self, having_param_list):
        self.__data['having'].extend(having_param_list)

    def extend_having_linker_op(self, having_linker_op_list):
        self.__data['having_linker_op_list'].extend(having_linker_op_list)

    def add_having_linker_op(self, having_linker_op):
        self.__data['having_linker_op_list'].append(having_linker_op)

    def set_limit_param(self, limit_param):
        self.__data['limit'] = limit_param

    def add_linker_op(self, linker_op):
        self.__data['linker_op_list'].append(linker_op)

    def extend_linker_op(self, linker_op_list):
        self.__data['linker_op_list'].extend(linker_op_list)

    @staticmethod
    def make_where_sql_clause(params_data, linker_op_data):
        str_noraml_param_list = list()
        param_table_list = list()
        for p in params_data:
            op = p[1].lower()
            if isinstance(p[2], SelectClauseParam):
                tmp_list = []
                tmp_list.append('%s %s ' % (p[0], op))
                tmp_list.append('(')
                tmp_list.append(p[2][0])
                tmp_list.append(')')
                str_noraml_param_list.append(''.join(tmp_list))
                param_table_list.extend(p[2][1])
                continue
            if not p[3]:
                str_noraml_param_list.append('%s %s %s' % (p[0], op, p[2]))
                continue
            in_flags = False if op.find('in') == -1 else True
            between_flags = False if op.find('between') == -1 else True
            if not in_flags and not between_flags:
                str_noraml_param_list.append('%s %s %%s' % (p[0], op))
                param_table_list.append(p[2])
                continue
            else:
                if isinstance(p[2], list) or isinstance(p[2], tuple):
                    param_list = list(p[2])
                else:
                    param_list = p[2].split(',')
                if between_flags:
                    if len(param_list) == 1:
                        param_list = param_list * 2
                    param_list = param_list[:2]
                    str_noraml_param_list.append('%s %s %s' % (p[0], op, ' and '.join(['%s'] * len(param_list))))
                else:
                    str_noraml_param_list.append('%s %s (%s)' % (p[0], op, ', '.join(['%s'] * len(param_list))))
                param_table_list.extend(param_list)
        normal_param_list_count = len(str_noraml_param_list)
        copy_linker_op_data = [op for op in linker_op_data]
        while len(copy_linker_op_data) < normal_param_list_count:
            copy_linker_op_data.append('and')

        result_list = list()
        for i in range(len(str_noraml_param_list)):
            result_list.append(str_noraml_param_list[i])
            result_list.append(copy_linker_op_data[i])
        result_list.pop()

        return (' '.join(result_list), param_table_list)

    @staticmethod
    def make_having_sql_clause(params_data, linker_op_data):
        result_list = []
        result_list.append(' having ')
        (sql, params) = SqlParamCollections.make_where_sql_clause(params_data, linker_op_data)
        result_list.append(sql)
        return (''.join(result_list), params)

    @staticmethod
    def make_orderby_sql_clause(data):
        result_list = []
        result_list.append(' order by')
        orderby_clause_list = []
        for p in data:
            if isinstance(p, tuple) and len(p) == 2:
                orderby_clause_list.append('%s %s' % (p[0], p[1]))
            else:
                orderby_clause_list.append(p)
        result_list.append(', '.join(orderby_clause_list))
        return (' '.join(result_list), [])

    @staticmethod
    def make_groupby_sql_clause(data):
        result_list = []
        result_list.append(' group by ')
        result_list.append(', '.join([p for p in data]))
        return (''.join(result_list), [])

    @staticmethod
    def make_limit_sql_clause(data):
        if isinstance(data[0], tuple):
            copy_limit_param = [op for op in list(data[0])]
        else:
            copy_limit_param = [op for op in data]
        if len(copy_limit_param) != 2:
            copy_limit_param.insert(0, 0)
        return (' limit %s, %s' % (copy_limit_param[0], copy_limit_param[1]), [])

    def can_add_where(self):
        return len(self.__data['normal_param'])

    def get_where_sql(self):
        result_list = []
        result_params = []
        sql_key_word = ['normal_param', 'group_by', 'having', 'order_by', 'limit']
        for k in sql_key_word:
            if len(self.__data[k]) != 0:
                (sql, params) = self.make_functions[k]()
                result_list.append(sql)
                result_params.extend(params)
        return (''.join(result_list), result_params)

def make_example():
    sql_params = SqlParamCollections(
        normal_param_list=[
            ('A','=', 1, True), 
            ('B', '<', 2, True),
            ('time','between',[1, 2], True),
            ('C','not in',[1, 3, 4], True)
        ], 
        group_by_param_list=[
            'B'
        ], 
        having_param_list=[
            ('A', '>', 100, True), 
            ('B', '!=', 2, True)
        ], 
        having_linker_op=[
            'or'
        ], 
        order_by_param_list=[
            ('B', 'asc'), 
            ('A', 'desc')
        ], 
        normal_linker_op_list=[
            'or', 
            'or'
        ],
        limit_param=(20))
    print(sql_params.get_where_sql())
    sql_params = SqlParamCollections(
        normal_param_list=[
            ('A','=', 1, True), 
            ('B', '<', 2, True)]
        )
    print(sql_params.get_where_sql())

def main():
    make_example()

if __name__ == '__main__':
    main()
