# -*- coding:utf-8 -*-

from DatabaseLibrary.connection_manager import ConnectionManager
from DatabaseLibrary.query import Query
from DatabaseLibrary.assertion import Assertion
from SCLibrary.base import keyword
import json

class DBKeywords(ConnectionManager, Query, Assertion):

    @keyword("DB Connect")
    def db_connect_to_mysql(self, db):
        """ 连接数据库
        ``db`` 字典，例：{'db':'mysql','host':'172.17.40.214','port=7003','name=todo','user':'root','pwd':'root'}
        其中db为连接的数据库类型名称，默认mysql,  name为数据库名
        """
        module = db['db'] if 'db' in db else 'pymysql'
        if module.upper() == 'MYSQL':
            module = 'pymysql'
        elif module.upper() == 'POSTGRESQL' or module.upper() == 'PGSQL':
            module = 'psycopg2'
        super(DBKeywords, self).connect_to_database(dbapiModuleName=module, dbName=db['name'],
                                                    dbUsername=db['user'], dbPassword=db['pwd'], dbHost=db['host'], dbPort=db['port'], dbCharset='utf8')

    @keyword("DB Disconnect From Database")
    def db_disconnect_db(self):
        """ 断开所有的数据库连接 """
        super(DBKeywords, self).disconnect_from_database()

    @keyword("DB Query")
    def db_query(self, selectStatement, sansTran=False, returnAsDict=True):
        """ 连接数据库
        ``selectStatement``  select语句
        
        ``sansTran`` 是否处于事务

        ``returnAsDict`` 结果作为字典返回，默认True
        """
        return super(DBKeywords, self).query(selectStatement, sansTran, returnAsDict)

    @keyword("DB Execute Sql Script")
    def db_execute_sql_script(self, sqlScriptFileName, sansTran=False):
        """ 执行一个SQL脚本文件
        ``sqlScriptFileName``  脚本目录
        
        ``sansTran`` 是否处于事务
        """
        super(DBKeywords, self).execute_sql_script(sqlScriptFileName, sansTran)

    @keyword("DB Execute Sql String")
    def db_execute_sql_string(self, sqlString, sansTran=False):
        """ 执行一个SQL
        ``sqlString``  sql
        
        ``sansTran`` 是否处于事务
        """
        super(DBKeywords, self).execute_sql_string(sqlString, sansTran)

    @keyword("DB Check If Exists In Database")
    def db_exists_in_db(self, selectStatement, sansTran=False):
        """ 断言查询结果是否存在
        ``selectStatement``  查询语句
        
        ``sansTran`` 是否处于事务
        """
        super(DBKeywords, self).check_if_exists_in_database(selectStatement, sansTran)

    @keyword("DB Check If Not Exists In Database")
    def db_not_exists_in_db(self, selectStatement, sansTran=False):
        """ 断言查询结果是否不存在 """
        super(DBKeywords, self).check_if_not_exists_in_database(selectStatement, sansTran)