#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Date    : 2018-8-6 15:40:03
# @Author  : datachain

import pymysql
import logging

class Mysql:
    log = None
    __db = None

    def __init__(self, host, port, userName, passwd, dbName):
        self.log = logging.getLogger()
        try:
            self.__db = pymysql.connect(host = host, port = port,user = userName, passwd = passwd, db = dbName)
        except Exception as e:
            self.log.error("connect db error %s" %e)

    def getDb(self):
        if self.__db != None:
            return self.__db
        else:
            self.log.error("db is not init")
            return None

    def queryDb(self, sql):
        cursor = self.__db.cursor()
        try:
            cursor.execute(sql)
            results = cursor.fetchall()
            return results
        except Exception as e:
            self.log.error("queryDb error  is %s " %e)

    def modifyDb(self, sql):
        cursor = self.__db.cursor()
        try:
            cursor.execute(sql)
            cursor.fetchall()
            self.__db.commit()
        except Exception as e:
            self.log.error("modifyDb error  is %s " %e)
            self.__db.rollback()

    def closeDb(self):
        try:
            self.__db.close()
        except Exception as e:
            self.log.error("closeDb error is %s" %e)