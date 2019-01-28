#! /usr/bin/env python3
# -*- coding: utf-8 -*-

"""
@Version : python3.6
@Author  : LiuSQ
@Time    : 2019/1/28 13:46
@Describe: 
"""
import cx_Oracle

# ora格式demo

# ora_tns = '(DESCRIPTION =(ADDRESS_LIST =(ADDRESS = (PROTOCOL = TCP)(HOST = 10.18.32.122)(PORT = 1521)))(
# CONNECT_DATA =(SERVER = DEDICATED)(' \ 'SERVICE_NAME = zactstdb))) '
import pyodbc

import pymysql


class OracleHelper:
    """
        oracle工具类
    """

    def __init__(self, user_name="", password="", ora=""):
        self.connect = cx_Oracle.connect(user_name, password, ora)
        self.instance = self.connect.cursor()

    def select_oracle_fetchone(self, select_statement):
        """
        查询oracle数据库，返回第一个查询到的结果
        :param select_statement:
        :return:
        """
        self.instance.execute(select_statement)
        select_result = self.instance.fetchone()
        return select_result

    def select_oracle_fetchall(self, select_statement):
        """
        查询oracle数据库，返回全部查询到的结果
        :param select_statement:
        :return:
        """
        self.instance.execute(select_statement)
        select_result = self.instance.fetchall()
        return select_result

    def update_oracle(self, update_statement):
        """
        根据入参语句，更新数据库
        :param update_statement:
        """
        self.instance.execute(update_statement)
        self.connect.execute("commit")


# 初始化传参demo
#  DRIVER={SQL Server};SERVER=172.20.3.4;PORT=1433;DATABASE=Tout_ZAESD;UID=sa;PWD=Za888888


class SqlServerHelper:
    """
       sql Server数据库工具类
    """

    def __init__(self, connect_statement=""):
        self.connect = pyodbc.connect(connect_statement)
        self.instance = self.connect.cursor()

    def select_sql_fetchone(self, select_statement):
        """
        查询sql Server数据库，返回第一个查询到的结果
        :param select_statement:
        :return:
        """
        self.instance.execute(select_statement)
        select_result = self.instance.fetchone()
        return select_result

    def select_sql_fetchall(self, select_statement):
        """
        查询sql Server数据库，返回全部查询到的结果
        :param select_statement:
        :return:
        """
        self.instance.execute(select_statement)
        select_result = self.instance.fetchall()
        return select_result

    def update_sql(self, update_statement):
        """
        根据入参语句，更新数据库
        :param update_statement:
        """
        self.instance.execute(update_statement)
        self.connect.execute("commit")


# 初始化入参demo
# host='10.18.33.1', port=3306, user='mgr', passwd='8lB6XoJm72oE#',db='customer_member', charset='utf8'
class MySqlHelper:
    """
        mysql数据库工具类
    """

    def __init__(self, host="", port=3306, user="", password="", db="", charset='utf8'):
        self.connect = pymysql.Connect(host=host, port=port, user=user, passwd=password, db=db, charset=charset)
        self.instance = self.connect.cursor()

    def select_mysql_fetchone(self, select_statement):
        """
        查询MySql数据库，返回第一个查询到的结果
        :param select_statement:
        :return:
        """
        self.instance.execute(select_statement)
        select_result = self.instance.fetchone()
        return select_result

    def select_mysql_fetchall(self, select_statement):
        """
        查询MySql数据库，返回全部查询到的结果
        :param select_statement:
        :return:
        """
        self.instance.execute(select_statement)
        select_result = self.instance.fetchall()
        return select_result

    def update_mysql(self, update_statement):
        """
        根据入参语句，更新数据库
        :param update_statement:
        """
        self.instance.execute(update_statement)
        self.connect.execute("commit")
