#!/usr/bin/python
# -*- coding: utf-8 -*-

import time
import traceback

'''Gibt die Ereignisse zurück'''
def get_events(username, type, limit, offset, db):
    params = {'limit':limit, 'offset':offset}

    where_clause = ""

    if type is not None and type != "":
        params['type'] = type
        where_clause = "WHERE TYPE == :type "

    with db:
        cur = db.cursor()
        cur.execute("SELECT * FROM 'EVENTS' "+where_clause+"ORDER BY TIMESTAMP DESC LIMIT :limit OFFSET :offset", params)

        events = []

        for data in cur.fetchall():
            item = {'text': data['TEXT'], 'time': data['TIMESTAMP'], 'type': data['TYPE']}
            events.append(item)

        #EVENTS_LAST_CHECKED mit aktueller Zeit aktualisieren
        cur.execute("UPDATE 'userdata' SET 'EVENTS_LAST_CHECKED' = :time WHERE USERNAME == :username",
            {'time': time.time(), 'username': username})

        return {'events': events}

'''Gibt die Anzahl der ungesehenen Ereignisse zurück'''
def get_unseen_events(username, db):
    last_checked = None

    with db:
        try:
            cur = db.cursor()
            cur.execute("SELECT EVENTS_LAST_CHECKED FROM 'userdata' WHERE USERNAME == :username",
                {'username': username})

            data = cur.fetchone()

            if data is not None:
                last_checked = data['EVENTS_LAST_CHECKED']
        except Exception as e:
            traceback.print_exc()
            print(str(e))

        if last_checked is not None:
            cur.execute("SELECT COUNT(*) FROM 'EVENTS' WHERE TIMESTAMP > :time",
                        {'time': last_checked})

            for data in cur.fetchall():
                return {'eventcount': data['COUNT(*)']}
        else:
            return {'status': 'usernotfound'}

'''Gibt die vorhandenen Ereignis-Typen zurück'''
def get_event_types(db):
    with db:
        cur = db.cursor()
        cur.execute("SELECT DISTINCT TYPE FROM EVENTS ORDER BY TYPE")

        types = []

        for data in cur.fetchall():
            types.append(data['TYPE'])

        return {'types': types}

'''Erstellt ein neues Ereignis'''
def add_event(type, text, db):
    with db:
        cur = db.cursor()
        cur.execute("INSERT INTO EVENTS (TYPE, TEXT, TIMESTAMP) VALUES (?,?,?)", [type, text, time.time()])
        return True