#!/usr/bin/env python3
# -*- coding:utf-8 -*-

from usqlite import *

db_fn="test.db"
udb = USQLite(db_fn)

q="""CREATE TABLE tmp ( id INTEGER PRIMARY KEY, 
                        name TEXT NOT NULL,
                        height REAL,
                        age INTEGER DEFAULT 0 );"""
if udb.create_table(q):
    print("created")
else:
    print("fail")


table_list = udb.get_table_names()
print(table_list)

column_list = udb.get_column_names("tmp")
print(column_list)

udb.assert_column( "tmp", "hi", "TEXT")
column_list = udb.get_column_names("tmp")
print(column_list)
