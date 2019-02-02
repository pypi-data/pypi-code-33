#!/usr/bin/python
# -*- coding: utf-8 -*-
from homevee.Functions.sensor_data import get_einheit
from homevee.Helper.helper_functions import has_permission
import datetime

'''Gibt den Sensorwerteverlauf für den gewünschten Zeitraum zurück'''
def get_graph_data(username, room, type, id, von, bis, db):

    if not has_permission(username, room, db):
        return {'status': 'nopermission'}

    if von == bis:
        datum = datetime.datetime.strptime(von, "%d.%m.%Y").strftime("%Y-%m-%d")

        return get_day_data(type, id, datum, db)
    else:
        return get_day_min_max(type, id, von, bis, db)

'''Gibt den Tageswerteverlauf des Sensors zurück'''
def get_day_data(type, id, datum, db):
    with db:
        cur = db.cursor()
        cur.execute("SELECT * FROM 'SENSOR_DATA' WHERE DEVICE_TYPE == :type AND DEVICE_ID == :id AND DATETIME >= :start AND DATETIME < :ende AND VALUE != \"N/A\" ORDER BY DATETIME ASC",
                    {'type':type, 'id':id, 'start':datum+" 00:00", 'ende':datum+" 23:59"});
        values = []

        for data in cur.fetchall():
            item = {'value':float(data['VALUE']), 'id':id, 'time':data['DATETIME'].replace(datum+" ","")}
            values.append(item)

        return {'values': values, 'einheit': get_einheit(type, id, db)}

'''Gibt die Höchst- & Tiefstwerte des angegebenen Datumsbereichs zurück'''
def get_day_min_max(type, id, von, bis, db):
    start = datetime.datetime.strptime(von, "%d.%m.%Y").strftime("%Y-%m-%d")
    ende = datetime.datetime.strptime(bis, "%d.%m.%Y").strftime("%Y-%m-%d")

    values = []

    with db:
        cur = db.cursor()
        cur.execute(
            "SELECT MIN(VALUE) as MIN, MAX(VALUE) as MAX, strftime(\"%d.%m.%Y\", DATETIME) as DATE FROM SENSOR_DATA WHERE DEVICE_TYPE == :type AND DEVICE_ID == :id AND DATETIME >= :start AND DATETIME <= :ende AND VALUE != \"N/A\" GROUP BY DATE ORDER BY DATETIME ASC",
            {'type': type, 'id': id, 'start': start+' 00:00', 'ende': ende+' 23:59'})

        #print {'type': type, 'id': id, 'start': start, 'ende': ende}

        for data in cur.fetchall():
            item = {'date':data['DATE'], 'min':data['MIN'], 'max':data['MAX']}

            values.append(item)

        return {'values':values, 'einheit': get_einheit(type, id, db)}