# coding；utf-8
import MySQLdb
import sys
class sqlapi:

    '''
    初始化
    '''
    def __init__(self, host_str, user_str, passwd_str, db_str):
        reconnect = 10
        while reconnect >0 :
            try:
                self.conn = MySQLdb.connect(host=host_str, user=user_str, passwd=passwd_str, db=db_str, charset="utf8")
            except:
                reconnect -= 1
                print(sys.exc_info())
            else:
                self.cursor = self.conn.cursor()
                return
    '''
    执行sql语句
    @输入：
        sqlstr:SQL语句
    '''
    def Run_Sql(self, sqlstr):
        date= -1
        try:
            date = self.cursor.execute(sqlstr)
        except:
            print(sqlstr)
            print(sys.exc_info())
        return date

    def GetOneDate(self):
        return self.cursor.fetchone()

    def GetAllDate(self, num):
        return self.cursor.fetchmany(num)

    def __del__(self):
        self.cursor.close()
        self.conn.commit()
        self.conn.close()


