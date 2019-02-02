#!/usr/bin/python
# -*- coding: utf-8 -*-
import sqlite3

import os


def dict_factory(cursor, row):
    d = {}
    for idx, col in enumerate(cursor.description):
        d[col[0]] = row[idx]
    return d

'''Gibt eine Instanz der Datenbankverbindung zurück'''
def get_database_con():
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    db_path = os.path.join(BASE_DIR, "data.db")

    #print db_path

    con = sqlite3.connect(db_path)
    con.text_factory = str
    con.row_factory = dict_factory

    return con

def get_server_data(key, db):
    with db:
        cur = db.cursor()

        cur.execute("SELECT VALUE FROM SERVER_DATA WHERE KEY = :key",
                    {'key': key})

        try:
            return cur.fetchone()['VALUE']
        except Exception, e:
            return None

def set_server_data(key, value, db):
    with db:
        cur = db.cursor()

        cur.execute("INSERT OR IGNORE INTO SERVER_DATA (VALUE, KEY) VALUES(:value, :key)",
                    {'value': value, 'key': key})

        cur.execute("UPDATE OR IGNORE SERVER_DATA SET VALUE = :value WHERE KEY = :key",
                    {'value': value, 'key': key})