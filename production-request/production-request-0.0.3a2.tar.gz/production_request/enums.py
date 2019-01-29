#!/usr/bin/env python
# -*- coding: utf-8 -*-


class SqlOperationEnum(object):
    u"""Типы операций в sql"""
    UNKNOWN = ''
    SELECT = 's'
    INSERT = 'i'
    UPDATE = 'u'
    DELETE = 'd'
    COMMIT = 'c'
    SAVEPOINT = 'sp'

    values = {
        SELECT: 'SELECT',
        INSERT: 'INSERT',
        UPDATE: 'UPDATE',
        DELETE: 'DELETE',
        COMMIT: 'COMMIT',
        SAVEPOINT: 'SAVEPOINT',
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