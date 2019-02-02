#!/usr/bin/python
# -*- coding: utf-8 -*-
import json

from homevee.Helper.helper_functions import has_permission


def add_edit_heating_scheme_item(username, id, time, value, active, days, data, db):
    if not has_permission(username, "admin", db):
        return {'status': 'noadmin'}

    with db:
        cur = db.cursor()

        params = {'time': time, 'value': value, 'active': active}

        if id == "" or id is None:
            cur.execute("INSERT INTO HEATING_SCHEME (TIME, VALUE, ACTIVE) VALUES (:time, :value, :active)",
                        params)

            id = cur.lastrowid
        else:
            params['id'] = id
            cur.execute("UPDATE HEATING_SCHEME SET TIME = :time, VALUE = :value, ACTIVE = :active WHERE ID = :id",
                params)

        #HEATING_SCHEME_DAYS bearbeiten
        cur.execute("DELETE FROM 'HEATING_SCHEME_DAYS' WHERE HEATING_SCHEME_ID = :id", {'id': id})

        day_array = json.loads(days)

        for day in day_array:
            cur.execute("INSERT INTO 'HEATING_SCHEME_DAYS' (HEATING_SCHEME_ID, WEEKDAY_ID) VALUES (:id, :weekday_id)",
                {'id': id, 'weekday_id': day})

        #HEATING_SCHEME_DEVICES bearbeiten
        cur.execute("DELETE FROM 'HEATING_SCHEME_DEVICES' WHERE ID = :id", {'id': id})

        device_array = json.loads(data)

        for device in device_array['devices']:
            cur.execute("INSERT INTO 'HEATING_SCHEME_DEVICES' (ID, LOCATION, TYPE, DEVICE_ID) VALUES (:id, :location, :type, :device_id)",
                {'id': id, 'location': device['location'], 'type': device['type'], 'device_id': device['id']})

        return {'status': 'ok'}

def delete_heating_scheme_item(username, id, db):
    if not has_permission(username, "admin", db):
        return {'status': 'noadmin'}

    params = {'id': id}

    queries = [
        "DELETE FROM HEATING_SCHEME WHERE ID = :id",
        "DELETE FROM HEATING_SCHEME_DAYS WHERE HEATING_SCHEME_ID = :id",
        "DELETE FROM HEATING_SCHEME_DEVICES WHERE ID = :id"
    ]

    with db:
        cur = db.cursor()

        for query in queries:
            cur.execute(query, params)

    cur.close()

    return {'status': 'ok'}

def get_heating_scheme_items(username, day, rooms, db):
    if not has_permission(username, "admin", db):
        return "noadmin"

    params = {'day': day}
    query_in_rooms_string = ""

    if rooms is not None and rooms != "":
        params['rooms'] = rooms
        query_in_rooms_string = "AND LOCATION IN (:rooms)"

    with db:
        cur = db.cursor()
        cur.execute("SELECT HEATING_SCHEME.ID, TIME, VALUE, ACTIVE, WEEKDAY_ID, ROOMS.NAME as LOCATION, TYPE, DEVICE_ID FROM HEATING_SCHEME, HEATING_SCHEME_DAYS, HEATING_SCHEME_DEVICES, ROOMS WHERE HEATING_SCHEME.ID = HEATING_SCHEME_DAYS.HEATING_SCHEME_ID AND HEATING_SCHEME.ID = HEATING_SCHEME_DEVICES.ID AND HEATING_SCHEME_DEVICES.LOCATION = ROOMS.LOCATION AND WEEKDAY_ID = :day "+query_in_rooms_string+" ORDER BY TIME",
                    params)

        heating_scheme_items = {}
        heating_scheme_data = {}

        results = cur.fetchall()

        for result in results:
            if result['ID'] not in heating_scheme_data:
                heating_scheme_data[result['ID']] = []

            heating_scheme_data[result['ID']].append({'location': result['LOCATION'], 'type': result['TYPE'], 'device':result['DEVICE_ID']})

            heating_scheme_items[result['ID']] = {'time': result['TIME'], 'value': result['VALUE'], 'isactive': (True if result['ACTIVE']=="true" else False)}

        for result in results:
            heating_scheme_items[result['ID']]['data'] = heating_scheme_data[result['ID']]

        cur.close()

        return {'heatingscheme': heating_scheme_items}

def get_heating_scheme_item_data(username, id, db):
    heating_scheme_item = {}

    params = {'id': id}


    with db:
        #Tage abfragen
        chosen_days = []
        cur = db.cursor()
        cur.execute("SELECT WEEKDAY_ID FROM HEATING_SCHEME_DAYS WHERE HEATING_SCHEME_ID == :id", params)
        for day in cur.fetchall():
            chosen_days.append(int(day['WEEKDAY_ID']))
        heating_scheme_item['days'] = chosen_days

        #Geräte abfragen
        devices = []
        cur.execute("SELECT * FROM HEATING_SCHEME_DEVICES WHERE ID == :id", params)
        for device in cur.fetchall():
            devices.append({'id': device['DEVICE_ID'], 'type': device['TYPE'], 'location': device['LOCATION']})
        heating_scheme_item['devicearray'] = json.dumps({'devices': devices})

        #Daten
        cur.execute("SELECT * FROM HEATING_SCHEME WHERE ID == :id", params)
        scheme_item_data = cur.fetchone()

        heating_scheme_item['value'] = float(scheme_item_data['VALUE'])
        heating_scheme_item['time'] = scheme_item_data['TIME']
        heating_scheme_item['active'] = scheme_item_data['ACTIVE']

        cur.close()

        return {'heatingschemeitem': heating_scheme_item}

def set_heating_scheme_item_active(username, id, active, db):
    if not has_permission(username, "admin", db):
        return {'status': 'noadmin'}

    with db:
        cur = db.cursor()
        cur.execute("UPDATE HEATING_SCHEME SET ACTIVE = :active WHERE ID = :id",
            {'active': active, 'id': id})

        cur.close()

        #Abfrage erfolgreich?
        if True:
            return {'status': 'ok'}
        else:
            return {'status': 'error'}

def is_heating_scheme_active(username, db):
    if not has_permission(username, "admin", db):
        return {'status': 'noadmin'}

    active = False

    with db:
        cur = db.cursor()
        cur.execute("SELECT * FROM SERVER_DATA WHERE KEY == 'HEATING_SCHEME_ACTIVE'")
        value = cur.fetchone()['VALUE']

        if value == "true":
            active = True

        cur.close()

        return {'isactive': active}

def set_heating_scheme_active(username, active, db):
    if not has_permission(username, "admin", db):
        return {'status': 'noadmin'}

    with db:
        cur = db.cursor()
        cur.execute("INSERT OR REPLACE INTO SERVER_DATA (KEY, VALUE) VALUES (:key, :value)",
            {'key': "HEATING_SCHEME_ACTIVE", 'value': active})

        cur.close()

        #Abfrage erfolgreich?
        if True:
            return {'status': 'ok'}
        else:
            return {'status': 'error'}