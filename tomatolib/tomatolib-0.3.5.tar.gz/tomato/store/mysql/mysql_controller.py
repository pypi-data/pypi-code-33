#!/usr/bin/python
# -*- coding:utf-8 -*-

"""
    @file:      mysql_controller.py
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    @auther:    zhouqinmin(zqm175899960@163.com)
    @date:      January 23, 2019
    @desc:      MysqlController
"""

#fit for normal add delete update select
import logging
import datetime
from tomato.store.mysql.mysql_model import MySqlModel
from tomato.store.mysql.sql_clause_assemble import BatchOperator
from tomato.store.mysql.sql_clause_assemble import SqlClauseAssemble


class MysqlController(object):
    __mysql_client = None
    def __init__(self):
        self.wanted_words = list()
        self.table_name = ''
        self.batch_clause_functions = dict()
        self.batch_clause_functions = {
            BatchOperator.INSERT: self._get_insert_clause,
            BatchOperator.DELETE: self._get_delete_clause,
            BatchOperator.UPDATE: self._get_update_clause,
            BatchOperator.SELECT: self._get_query_clause
        }

    @classmethod
    def set_mysql_client(cls, mysql_client):
        cls.__mysql_client = mysql_client

    async def parse_row(self, row):
        model = MySqlModel()
        for k, v in row.items():
            if isinstance(v, datetime.datetime):
                v = v.strftime("%Y-%m-%d %H:%M:%S")
            model.update({k: v})
        return model

    async def delete(self, where_params=None):
        (sql_clause, params) = self.execute_sql_clause(BatchOperator.DELETE, None, where_params)
        logging.info(((sql_clause, params)))
        result = await self.__mysql_client.execute(sql_clause, tuple(params))
        return result

    async def insert(self, mysql_model, where_params=None):
        (sql_clause, params) = self.execute_sql_clause(BatchOperator.INSERT, mysql_model, where_params)
        logging.info(((sql_clause, params)))
        result = await self.__mysql_client.execute(sql_clause, tuple(params))
        return result

    async def query(self, wanted_words=[], where_params=None):
        data_list = []
        (sql_clause, params) = self.execute_sql_clause(BatchOperator.SELECT, wanted_words, where_params)
        logging.info(((sql_clause, params)))
        result = await self.__mysql_client.get_all(sql_clause, tuple(params))
        if result is not None and len(result) > 0:
            for row in result:
                data = await self.parse_row(row)
                data_list.append(data)
        return data_list

    async def update(self, mysql_model, where_params=None):
        (sql_clause, params) = self.execute_sql_clause(BatchOperator.UPDATE, mysql_model, where_params)
        logging.info((sql_clause, params))
        result = await self.__mysql_client.execute(sql_clause, params)
        return result

    async def query_count(self, where_params=None):
        count = 0
        wanted_words = ['count(0)']
        result = await self.query(wanted_words, where_params)
        if result is not None and len(result) > 0:
            count = result[0]['count(0)']
        return count

    async def query_maxid(self, where_params=None):
        max_id = 0
        wanted_words = ['max(id)']
        result = await self.query(wanted_words, where_params)
        if result is not None and len(result) > 0:
            max_id = result[0]['max(id)']
        return max_id

    def execute_sql_clause(self, BatchOperator, mysql_model, where_params):
        return self.batch_clause_functions[BatchOperator](mysql_model, where_params)

    def _get_insert_clause(self, mysql_model, where_params):
        sql_assemble = SqlClauseAssemble()
        sql_assemble.table_name = self.table_name
        sql_assemble.insert_words = mysql_model.items()
        sql_assemble.where_params = where_params
        return sql_assemble.get_insert_clause()

    def _get_query_clause(self, wanted_words, where_params):
        sql_assemble = SqlClauseAssemble()
        sql_assemble.table_name = self.table_name
        sql_assemble.wanted_words = wanted_words \
            if wanted_words and len(wanted_words) != 0 else self.wanted_words
        sql_assemble.where_params = where_params
        return sql_assemble.get_query_clause()

    def _get_update_clause(self, mysql_model, where_params):
        sql_assemble = SqlClauseAssemble()
        sql_assemble.table_name = self.table_name
        sql_assemble.update_words = mysql_model.items()
        sql_assemble.where_params = where_params
        return sql_assemble.get_update_clause()

    def _get_delete_clause(self, mysql_model, where_params):
        sql_assemble = SqlClauseAssemble()
        sql_assemble.table_name = self.table_name
        sql_assemble.where_params = where_params
        return sql_assemble.get_delete_clause()
