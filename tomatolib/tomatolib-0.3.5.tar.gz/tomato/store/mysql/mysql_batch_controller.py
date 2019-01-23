#!/usr/bin/python
# -*- coding:utf-8 -*-

"""
    @file:      mysql_batch_controller.py
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    @auther:    zhouqinmin(zqm175899960@163.com)
    @date:      January 23, 2019
    @desc:      MysqlBatchController
"""

from tomato.util import singleton
from collections import namedtuple
from tomato.store.mysql.sql_clause_assemble import UnionType
from tomato.store.mysql.sql_clause_assemble import BatchOperator

MySqlBatchData = namedtuple('MySqlBatchData', ['Controller', 'Models', 'WhereParams', 'Method'])
BatchParams = namedtuple('BatchParams', ['sql_clause_param', 'batch_op'])

@singleton
class MysqlBatchController(object):
    __mysql_client = None
    union_strings = {UnionType.UNION: ' union ',
                    UnionType.UNION_ALL: ' union all '}

    def __init__(self, *args, **kwargs):
        pass

    @classmethod
    def set_mysql_client(cls, mysql_client):
        cls.__mysql_client = mysql_client

    async def insert_many_models(self, many_models, mysql_controller, where_params_list = None):
        data = MySqlBatchData(mysql_controller, many_models, where_params_list, BatchOperator.INSERT)
        result = await self.execute_batch([data])
        return result

    async def update_many_models(self, many_models, mysql_controller, where_params = None):
        data = MySqlBatchData(mysql_controller, many_models, where_params, BatchOperator.UPDATE)
        result = await self.execute_batch([data])
        return result

    async def execute_batch(self, mysql_batch_data_list):
        execute_batch_list = list()
        for data in mysql_batch_data_list:
            where_params = None
            if data.WhereParams is not None and isinstance(data.WhereParams, list):
                where_params = data.WhereParams
                execute_batch_list.extend([data.Controller.execute_sql_clause(data.Method, data.Models[i], where_params[i]) for i in range(len(data.Models))])
            else:
                where_params = data.WhereParams
                execute_batch_list.extend([data.Controller.execute_sql_clause(data.Method, model, where_params) for model in data.Models])
        result = await self.__mysql_client.execute_batch(execute_batch_list)
        return result

    async def execute_batch_params_list(self, batch_params_list):
        result = await self.__mysql_client.execute_batch([batch_param[0].execute_functions[batch_param[1]]() \
            for batch_param in batch_params_list])
        return result

    async def union(self, sql_clause_assemble_list, union_type):
        sql_list = list()
        sql_params = list()
        for sql_clause_assemble in sql_clause_assemble_list:
            (sql, params) = sql_clause_assemble.get_query_clause()
            sql_list.append(sql)
            sql_params.extend(params)
        result = await self.__mysql_client.get_all(self.union_strings[union_type].join(sql_list), sql_params)
        result_data = list()
        if result is not None and isinstance(result, list):
            result_data = [data for data in result]
        return result_data
