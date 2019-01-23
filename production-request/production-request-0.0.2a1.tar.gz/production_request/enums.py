#!/usr/bin/env python
# -*- coding: utf-8 -*-
from m3.db import BaseEnumerate


class SqlOperationEnum(BaseEnumerate):
    u"""Типы операций в sql"""
    UNKNOWN = ''
    SELECT = 's'
    INSERT = 'i'
    UPDATE = 'u'
    DELETE = 'd'

    values = {
        SELECT: 'SELECT',
        INSERT: 'INSERT',
        UPDATE: 'UPDATE',
        DELETE: 'DELETE',
    }

    @classmethod
    def get_key_by_sql(cls, sql):
        u"""
        Возвращает ключ операции по sql-запросу
        :param sql: sql-запрос
        :rtype: str
        """
        for key, value in cls.values.items():
            if value in sql:
                result = key
                break
        else:
            result = cls.UNKNOWN

        return result