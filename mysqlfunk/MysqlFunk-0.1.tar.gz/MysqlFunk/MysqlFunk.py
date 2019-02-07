#! python3.7

import mysql.connector
import traceback



class MysqlFunk:
    '''
    notes
    '''
    def __init__(self,**kwargs):
        self.dbconfig = {
            'user': kwargs.get('user'),
            'password': kwargs.get('password',None),
            'host': kwargs.get('host'),
            'database': kwargs.get('database')
                }

    def query_statement(self, statement):
        cnx = mysql.connector.connect(**self.dbconfig)
        dbcur = cnx.cursor()
        try:
            dbcur.execute(statement)
            cursorReadout = dbcur.fetchall()
        except :
            print("Problem executing statement: %s" % (statement))
            traceback.print_exc()
            cursorReadout = []
        dbcur.close()
        cnx.close()
        return cursorReadout

    def commit_statement(self, statement):
        cnx = mysql.connector.connect(**self.dbconfig)
        dbcur = cnx.cursor()
        try:
            dbcur.execute(statement)
            cnx.commit()        
        except :
            print("Problem executing statement: %s" % (statement))
            traceback.print_exc()
        return