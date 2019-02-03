#!/usr/bin/python
# # -*- coding: utf-8 -*-
import datetime
from time import sleep

from homevee.db_utils import get_database_con
from homevee.device_types import *


def save_energy_data(db):
    with db:
        cur = db.cursor()

        date_now = datetime.datetime.now()
        date = date_now.strftime('%Y-%m-%d %H:%M')

        total_value = 0

        room_total_value = {}

        # Z-Wave Stromzähler
        cur.execute("SELECT * FROM ZWAVE_POWER_METER")
        for item in cur.fetchall():
            room_id = item['ROOM_ID']
            value = save_to_db(date_now, ZWAVE_POWER_METER, room_id, item['DEVICE_ID'],
                               item['VALUE'], db)
            total_value += value

            if room_id in room_total_value:
                room_total_value[room_id] += value
            else:
                room_total_value[room_id] = value

        #Gesamtwerte der Räume speichern
        for room in room_total_value:
            print "inserting in room_energy_data of room: "+str(room)
            cur.execute("INSERT INTO ROOM_ENERGY_DATA (ROOM_ID, POWER_USAGE, DATE) VALUES (:room, :usage, :date)",
                        {'room': room, 'usage': room_total_value[room_id], 'date': date})

        #Gesamtverbrauch speichern
        print "inserting in energy_data"
        cur.execute("INSERT INTO ENERGY_DATA (DATE, POWER_USAGE) VALUES (:date, :value)",
                    {'date': date, 'value': total_value})

def save_to_db(date_now, type, room_id, id, value, db):
    value = float(value)

    with db:
        cur = db.cursor()
        date = date_now.strftime('%Y-%m-%d %H:%M')

        if type == ZWAVE_POWER_METER:
            cur.execute("SELECT PREV_VALUE FROM ZWAVE_POWER_METER WHERE DEVICE_ID = :id", {'id': id})
            result = cur.fetchone()
            prev_value = float(result['PREV_VALUE'])

            prev_value = prev_value+value
            print "prev_value: "+str(prev_value)
            print "updating zwave_power_meter value"
            cur.execute("UPDATE ZWAVE_POWER_METER SET PREV_VALUE = :val, VALUE = 0 WHERE DEVICE_ID = :id",
                {'val': prev_value, 'id': id})

        print "inserting in device_energy_data"
        cur.execute("INSERT INTO DEVICE_ENERGY_DATA (LOCATION, DEVICE_ID, DEVICE_TYPE, DATE, POWER_USAGE) \
                        VALUES (:location, :id, :type, :date, :value)",
                    {'location': room_id, 'id': id, 'type': type, 'date': date, 'value': value})

        return value

def init_thread():
    print "energy saving thread initiated"
    while True:
        db = get_database_con()

        t = datetime.datetime.today()

        seconds_to_wait = (24 * 60 * 60) - (t.hour * 60 * 60) - (t.minute * 60) - t.second - 60 #um 23:59 ausführen
        #seconds_to_wait = 5
        print "waiting for "+str(seconds_to_wait)+" seconds"
        sleep(seconds_to_wait)
        print("Saving Energy-data")
        save_energy_data(db)
