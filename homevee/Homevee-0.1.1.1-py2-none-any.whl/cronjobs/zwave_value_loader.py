#!/usr/bin/python
# -*- coding: utf-8 -*-
from time import sleep

from homevee.DeviceAPI.zwave.get_devices import set_device_value
from homevee.DeviceAPI.zwave.utils import do_zwave_request
from homevee.db_utils import get_database_con
from homevee.device_types import *

def load_zwave_values(db):
    with db:
        cur = db.cursor()

        # Alle Z-Wave Gerätetypen durchlaufen und den aktuellen Wert in Datenbank schreiben

        #Stromzähler
        TYPE = ZWAVE_POWER_METER
        cur.execute("SELECT * FROM ZWAVE_POWER_METER")
        data = cur.fetchall()

        for item in data:
            ID = item['DEVICE_ID']
            result = do_zwave_request("/ZAutomation/api/v1/devices/" + ID, db)

            if result['code'] != 200:
                value = "N/A"
            else:
                value = result['data']['metrics']['level']

            set_device_value(TYPE, ID, value, db)

        #Thermostat
        TYPE = ZWAVE_THERMOSTAT
        cur.execute("SELECT * FROM ZWAVE_THERMOSTATS")
        data = cur.fetchall()

        for item in data:
            ID = item['THERMOSTAT_ID']
            result = do_zwave_request("/ZAutomation/api/v1/devices/" + ID, db)

            if result['code'] != 200:
                value = "N/A"
            else:
                value = result['data']['metrics']['level']

            set_device_value(TYPE, ID, value, db)

        #Sensor
        TYPE = ZWAVE_SENSOR
        cur.execute("SELECT * FROM ZWAVE_SENSOREN")
        data = cur.fetchall()

        for item in data:
            ID = item['ID']
            result = do_zwave_request("/ZAutomation/api/v1/devices/" + ID, db)

            if result['code'] != 200:
                value = "N/A"
            else:
                value = result['data']['metrics']['level']

                #if item['VALUE'] != value:
                    #trigger automation

            set_device_value(TYPE, ID, value, db)

        #Schalter
        TYPE = ZWAVE_SWITCH
        cur.execute("SELECT * FROM ZWAVE_SWITCHES")
        data = cur.fetchall()

        for item in data:
            ID = item['ID']
            result = do_zwave_request("/ZAutomation/api/v1/devices/" + ID, db)

            if result['code'] != 200:
                value = "N/A"
            else:
                value = result['data']['metrics']['level']

                value = value == "on"

            set_device_value(TYPE, ID, value, db)

def init_thread():
    while True:
        db = get_database_con()
        load_zwave_values(db)
        db.close()
        sleep(5*60)