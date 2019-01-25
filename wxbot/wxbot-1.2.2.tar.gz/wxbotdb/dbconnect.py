# -*- coding:utf-8 -*-
__authon__ = "cfn@leapy.cn"

import sqlite3
import time
import sys

class db:
    def __init__(self):
        self.conn = sqlite3.connect('wxbot.db')
        self.curs = self.conn.cursor()
        self.init()
        pass

    def init(self):
        rows = self.curs.execute("select * from sqlite_master").fetchall()
        # print(rows)
        if len(rows) == 0:
            self.curs.execute(
                "create table wxsession(uin text, sid text, skey text, deviceID text, session text, uuid text, lang text, pass_ticket text, date text)")
            # self.curs.execute("create table wxcontact (name text, )")
            self.conn.commit()

    #   记录登录信息
    def saveLoginInfo(self, uin="", sid="", skey="", deviceID="", session="", uuid="",lang="",pass_ticket="",date=str(int(time.time()))):
        # print('insert into wxsession values("' + uin + '","' + sid + '","' + skey + '","' + deviceID + '","' + session + '","' + uuid +'","' + lang + '","' + pass_ticket + '","'+ + date +'")')
        rows = self.curs.execute("select * from wxsession where uin='"+uin+"'").fetchall()
        # print(self.curs.execute("select * from wxsession where uin='"+uin+"'").fetchall())
        if len(rows) == 0:
            self.curs.execute(
                'insert into wxsession values("' + uin + '","' + sid + '","' + skey + '","' + deviceID + '","' + session + '","' + uuid +'","' + lang + '","' + pass_ticket + '","' + date +'")')
        else:
            self.curs.execute('update wxsession set sid="'+ sid +'", skey="'+skey+'",deviceID="'+deviceID+'",session="'+session+'",uuid="'+uuid + '",lang="'+ lang + '",pass_ticket="'+ pass_ticket + '",date="'+date+'" where uin="'+uin+'"')
        self.conn.commit()

    def delLoginInfo(self,uin):
        self.curs.execute("delete from wxsession where uin='"+uin+"'")
        self.conn.commit()

    def getLoginInfo(self):
        return self.curs.execute("select * from wxsession order by date desc limit 0,1").fetchone()

    def close(self):
        self.conn.close()

# if __name__ == '__main__':
#     d = db()
#     info = d.getLoginInfo()
#     print(info)
#     d.close()










