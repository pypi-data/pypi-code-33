#!/usr/bin/python
# -*- coding:utf-8 -*-

"""
    @file:      sql_clause_assemble.py
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    @auther:    zhouqinmin(zqm175899960@163.com)
    @date:      January 23, 2019
    @desc:      SqlClauseAssemble
"""

from enum import Enum
from collections import namedtuple
from tomato.store.mysql.sql_param_collections import SelectClauseParam
from tomato.store.mysql.sql_param_collections import SqlParamCollections


class TableJoin(Enum):
    INNER_JOIN = 1
    LEFT_JOIN = 2
    RIGHT_JOIN = 3

class BatchOperator(Enum):
    INSERT = 1
    DELETE = 2
    UPDATE = 3
    SELECT = 4

class UnionType(Enum):
    UNION = 1
    UNION_ALL = 2

JoinParams = namedtuple('JoinParams', ['JoinTable', 'JoinType', 'JoinWhereParams'])


class SqlClauseAssemble(object):
    join_strings = {TableJoin.INNER_JOIN: 'inner join',
                    TableJoin.LEFT_JOIN: 'left join',
                    TableJoin.RIGHT_JOIN: 'right join'}
    def __init__(self, 
        wanted_words=[], 
        insert_words=[], 
        update_words=[], 
        join_param_list=[], 
        table_name=None, 
        where_params=None):
        self.__where_params = where_params #SqlParamCollections
        self.__wanted_words = wanted_words #[keys]
        self.__insert_words = insert_words #[(k, v)]
        self.__update_words = update_words #[(k, v)]
        self.__table_name = table_name #str
        self.__join_param_list = join_param_list
        self.__execute_functions = {
            BatchOperator.SELECT: self.get_query_clause,
            BatchOperator.INSERT: self.get_insert_clause,
            BatchOperator.UPDATE: self.get_update_clause,
            BatchOperator.DELETE: self.get_delete_clause
        }

    @property
    def execute_functions(self):
        return self.__execute_functions

    @property
    def join_param_list(self):
        return self.__join_param_list

    @join_param_list.setter
    def join_param_list(self, value):
        """where_params
        """
        self.__join_param_list = value

    @property
    def where_params(self):
        return self.__where_params

    @where_params.setter
    def where_params(self, value):
        """where_params
        """
        self.__where_params = value

    @property
    def update_words(self):
        return self.__update_words

    @update_words.setter
    def update_words(self, value):
        """__update_words
        """
        self.__update_words = value

    @property
    def insert_words(self):
        return self.__insert_words

    @insert_words.setter
    def insert_words(self, value):
        """insert_words
        """
        self.__insert_words = value

    @property
    def wanted_words(self):
        return self.__wanted_words

    @wanted_words.setter
    def wanted_words(self, value):
        """wanted_words
        """
        self.__wanted_words = value

    @property
    def table_name(self):
        return self.__table_name

    @table_name.setter
    def table_name(self, value):
        """wanted_words
        """
        self.__table_name = value

    def __make_insert_words_sql_clause(self):
        keys = [kv[0] for kv in self.__insert_words]
        values = [kv[1] for kv in self.__insert_words]
        return (', '.join(keys), values)

    def __make_update_words_sql_clause(self):
        keys = ['%s = %%s' % kv[0] for kv in self.__update_words]
        values = [kv[1] for kv in self.__update_words]
        return (', '.join(keys), values)

    def __make_wanted_words_sql_clause(self):
        return ', '.join(self.__wanted_words) if self.__wanted_words and len(self.__wanted_words) != 0 else '*'

    def __check_and_extract_noraml_param(self, where_params):
        normal_param = where_params.data['normal_param']
        for i in range(len(normal_param)):
            p = normal_param[i]
            if isinstance(p[2], SqlClauseAssemble):
                (sql, params) = p[2].get_query_clause()
                normal_param[i] = (p[0], p[1], SelectClauseParam(sql, params))

    def get_query_clause(self):
        result_list = []
        result_params = []
        result_list.append('select')
        result_list.append(self.__make_wanted_words_sql_clause())
        result_list.append('from')
        result_list.append(self.__table_name)

        if len(self.join_param_list) != 0:
            for join_param in self.join_param_list:
                result_list.append(self.join_strings[join_param[1]])
                result_list.append(join_param[0])
                if join_param[2] is not None:
                    result_list.append('on')
                    (join_sql, join_params) = join_param[2].get_where_sql()
                    result_list.append(join_sql)
                    result_params.extend(join_params)

        if self.__where_params is not None:
            if self.__where_params.can_add_where():
                result_list.append('where')
                self.__check_and_extract_noraml_param(self.__where_params)
            (where_sql, params) = self.__where_params.get_where_sql()
            result_list.append(where_sql)
            result_params.extend(params)
        return (' '.join(result_list), result_params)

    def get_insert_clause(self):
        result_list = []
        result_params = []
        result_list.append('insert into')
        result_list.append(self.__table_name)
        result_list.append('(')
        (insert_words, insert_values) = self.__make_insert_words_sql_clause()
        result_list.append(insert_words)
        result_params.extend(insert_values)
        result_list.append(')')
        result_list.append('values(')
        result_list.append(', '.join(['%s'] * len(result_params)))
        result_list.append(')')
        if self.__where_params is not None and self.__where_params.can_add_where():
            result_list.append('ON DUPLICATE KEY UPDATE')
            if len(self.__where_params.data['linker_op_list']) == 0:
                self.__where_params.data['linker_op_list'].extend(len(self.__where_params.data['normal_param']) * [', '])
            (where_sql, params) = self.__where_params.get_where_sql()
            result_list.append(where_sql)
            result_params.extend(params)
        return (' '.join(result_list), result_params)

    def get_update_clause(self):
        result_list = []
        result_params = []
        result_list.append('update')
        result_list.append(self.__table_name)
        result_list.append('set')
        (update_words, update_values) = self.__make_update_words_sql_clause()
        result_list.append(update_words)
        result_params.extend(update_values)
        if self.__where_params is not None:
            if self.__where_params.can_add_where():
                result_list.append('where')
                self.__check_and_extract_noraml_param(self.__where_params)
            (where_sql, params) = self.__where_params.get_where_sql()
            result_list.append(where_sql)
            result_params.extend(params)
        return (' '.join(result_list), result_params)

    def get_delete_clause(self):
        result_list = []
        result_params = []
        result_list.append('delete from')
        result_list.append(self.__table_name)
        if self.__where_params is not None:
            if self.__where_params.can_add_where():
                result_list.append('where')
                self.__check_and_extract_noraml_param(self.__where_params)
            (where_sql, params) = self.__where_params.get_where_sql()
            result_list.append(where_sql)
            result_params.extend(params)
        return (' '.join(result_list), result_params)

def make_query_clause():
    id_sql_assemble = SqlClauseAssemble()
    id_sql_assemble.wanted_words = ['id', 'min(id)']
    id_sql_assemble.table_name = 'Persons'
    id_sql_assemble.where_params = SqlParamCollections(
        normal_param_list=[
            ('age', '<', 35, True),
            ('Year', 'in', (2012, 2013, 2015), True)
            ]
    )

    sql_assemble = SqlClauseAssemble()
    sql_assemble.wanted_words = ['name']
    sql_assemble.table_name = 'Persons'
    sql_assemble.where_params = SqlParamCollections(
        normal_param_list=[
            ('name', '=', 'zhouqinmin', True),
            ('id', 'in', id_sql_assemble, True)
            ]
    )

    total_sql_assemble = SqlClauseAssemble()
    total_sql_assemble.wanted_words = ['name']
    total_sql_assemble.table_name = 'Persons'
    total_sql_assemble.where_params = SqlParamCollections(
        normal_param_list=[
            ('Year', '>', 1965, True),
            ('name', 'in', sql_assemble, True)
            ],
        order_by_param_list = [('age'), ('name', 'desc')],
        group_by_param_list=[('age'), ('Year')]
    )

    print(total_sql_assemble.get_query_clause())

def make_insert_clause():
    sql_assemble = SqlClauseAssemble()
    sql_assemble.insert_words = [('LastName', 'Gates'), ('FirstName', 'Bill'), 
        ('Address', 'Xuanwumen 10'), ('City', 'Beijing')]
    sql_assemble.table_name = 'Persons'
    print(sql_assemble.get_insert_clause())

def make_update_clause():
    sql_assemble_1 = SqlClauseAssemble()
    sql_assemble_1.wanted_words = ['name']
    sql_assemble_1.table_name = 'Persons'
    sql_assemble_1.where_params = SqlParamCollections(
        normal_param_list=[
            ('id', '=', '1', True),
            ]
    )

    id_sql_assemble = SqlClauseAssemble()
    id_sql_assemble.wanted_words = ['id']
    id_sql_assemble.table_name = 'Persons'
    id_sql_assemble.where_params = SqlParamCollections(
        normal_param_list=[
            ('Year', '>', 1965, True),
            ('name', 'in', sql_assemble_1, True)
            ]
    )

    sql_assemble = SqlClauseAssemble()
    sql_assemble.update_words = [('Address', 'Zhongshan 23'), ('City', 'Nanjing')]
    sql_assemble.table_name = 'Person'
    sql_assemble.where_params = SqlParamCollections(
        normal_param_list=[
            ('LastName', '=', 'Wilson', True),
            ('id', 'not in', id_sql_assemble, True)
            ]
    )
    print(sql_assemble.get_update_clause())

def make_delete_clause():
    id_sql_assemble = SqlClauseAssemble()
    id_sql_assemble.wanted_words = ['id']
    id_sql_assemble.table_name = 'Persons'
    id_sql_assemble.where_params = SqlParamCollections(
        normal_param_list=[
            ('Year', '>', 1965, True)
            ]
    )

    sql_assemble = SqlClauseAssemble()
    sql_assemble.table_name = 'Person'
    sql_assemble.where_params = SqlParamCollections(
        normal_param_list=[
            ('id', 'in', id_sql_assemble, True),
            ('LastName', '=', 'Wilson', True)
            ]
    )
    print(sql_assemble.get_delete_clause())

def make_join_query_clause():
    sql_assemble = SqlClauseAssemble()
    sql_assemble.wanted_words = ['name']
    sql_assemble.table_name = 'Persons'
    sql_assemble.where_params = SqlParamCollections(
        normal_param_list=[
            ('name', '=', 'zhouqinmin', True)
        ]
    )

    sql_assemble.join_param_list = \
    [('Student', TableJoin.LEFT_JOIN, SqlParamCollections(normal_param_list=[('Persons.id', '=', 'Student.id', False)])),
    ('Student', TableJoin.LEFT_JOIN, SqlParamCollections(normal_param_list=[('Persons.id', '=', 'Student.id', False)]))]

    print(sql_assemble.get_query_clause())

def main():
    make_query_clause()
    make_insert_clause()
    make_update_clause()
    make_delete_clause()
    make_join_query_clause()

if __name__ == '__main__':
    main()
