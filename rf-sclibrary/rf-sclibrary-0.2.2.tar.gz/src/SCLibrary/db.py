# -*- coding:utf-8 -*-

from DatabaseLibrary.connection_manager import ConnectionManager
from DatabaseLibrary.query import Query
from DatabaseLibrary.assertion import Assertion
from base import keyword
import json

class DBKeywords(ConnectionManager, Query, Assertion):

    @keyword("DB Connect")
    def db_connect_to_mysql(self, db):
        module = db['db'] if db.has_key('db') else 'pymysql'
        if(module.upper() == 'MYSQL'):
            module = 'pymysql'
        super(DBKeywords, self).connect_to_database(dbapiModuleName=module, dbName=db['name'],
                                                    dbUsername=db['user'], dbPassword=db['pwd'], dbHost=db['host'], dbPort=db['port'], dbCharset='utf8')

    @keyword("DB Disconnect From Database")
    def db_disconnect_db(self):
        super(DBKeywords, self).disconnect_from_database()

    @keyword("DB Query")
    def db_query(self, selectStatement, sansTran=False, returnAsDict=True):
        return super(DBKeywords, self).query(selectStatement, sansTran, returnAsDict)

    @keyword("DB Execute Sql Script")
    def db_execute_sql_script(self, sqlScriptFileName, sansTran=False):
        super(DBKeywords, self).execute_sql_script(sqlScriptFileName, sansTran)

    @keyword("DB Execute Sql String")
    def db_execute_sql_string(self, sqlString, sansTran=False):
        super(DBKeywords, self).execute_sql_string(sqlString, sansTran)

    @keyword("DB Check If Exists In Database")
    def db_exists_in_db(self, selectStatement, sansTran=False):
        super(DBKeywords, self).check_if_exists_in_database(selectStatement, sansTran)

    @keyword("DB Check If Not Exists In Database")
    def db_not_exists_in_db(self, selectStatement, sansTran=False):
        super(DBKeywords, self).check_if_not_exists_in_database(selectStatement, sansTran)