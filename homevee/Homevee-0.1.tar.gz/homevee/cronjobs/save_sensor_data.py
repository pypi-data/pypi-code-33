#!/usr/bin/python
# -*- coding: utf-8 -*-
import datetime
from time import sleep

from homevee.db_utils import get_database_con
from homevee.device_types import *

def save_sensor_data(db):
    with db:
        cur = db.cursor()

        #Z-Wave Sensoren
        cur.execute("SELECT * FROM ZWAVE_SENSOREN")
        for item in cur.fetchall():
            if item['SAVE_DATA']:
                save_to_db(ZWAVE_SENSOR, item['ID'], item['VALUE'], db)
                
        #MQTT Sensoren
        cur.execute("SELECT * FROM MQTT_SENSORS")
        for item in cur.fetchall():
            if item['SAVE_DATA']:
                save_to_db(MQTT_SENSOR, item['ID'], item['LAST_VALUE'], db)

def save_to_db(type, id, value, db):
    with db:
        time = datetime.datetime.now().strftime('%Y-%m-%d %H:00')

        cur = db.cursor()

        cur.execute("INSERT INTO SENSOR_DATA (DEVICE_ID, DEVICE_TYPE, DATETIME, VALUE) \
                        VALUES (:id, :type, :time, :value)",
                    {'id': id, 'type': type, 'time': time, 'value':value})

def init_thread():
    while True:
        db = get_database_con()

        t = datetime.datetime.today()

        seconds_to_wait = (60*60) - (t.minute*60) - t.second
        sleep(seconds_to_wait)
        print("Saving sensor-data")
        save_sensor_data(db)
