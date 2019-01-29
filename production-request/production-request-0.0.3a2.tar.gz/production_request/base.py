#!/usr/bin/env python
# -*- coding: utf-8 -*-
try:
    from django.db.backends import util as utils
except ImportError:
    from django.db.backends import utils
from django.db.backends.postgresql_psycopg2 import base

from production_request.utils import calc_sql_metrics


class CursorWrapper(utils.CursorWrapper):
    """
    Враппер курсора БД для подсчета времени выполнения запроса
    """
    def execute(self, sql, params=None):
        with calc_sql_metrics(self, sql):
            return self.cursor.execute(sql, params)

    def executemany(self, sql, param_list):
        with calc_sql_metrics(self, sql):
            return self.cursor.executemany(sql, param_list)


class DatabaseWrapper(base.DatabaseWrapper):
    """
    Враппер БД с кастомным курсором
    """
    def cursor(self):
        if hasattr(self, 'validate_thread_sharing'):
            self.validate_thread_sharing()
        cursor = CursorWrapper(self._cursor(), self)
        return cursor

    def _commit(self):
        with calc_sql_metrics(self.cursor(), 'COMMIT'):
            return super(DatabaseWrapper, self)._commit()