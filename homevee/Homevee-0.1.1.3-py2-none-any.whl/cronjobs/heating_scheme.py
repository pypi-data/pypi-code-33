#!/usr/bin/python
# -*- coding: utf-8 -*-
import datetime
import time

from homevee.DeviceAPI.heating import heating_control
from homevee.db_utils import get_database_con


def run_heating_scheme():
    db = get_database_con()

    current_datetime = datetime.datetime.now()

    with db:
        cur = db.cursor()

        #Query heating scheme for this day and time
        query = 'SELECT * FROM HEATING_SCHEME, HEATING_SCHEME_DAYS, HEATING_SCHEME_DEVICES WHERE HEATING_SCHEME.ID = HEATING_SCHEME_ID AND HEATING_SCHEME.ID = HEATING_SCHEME_DEVICES.ID AND ACTIVE = "true" AND TIME = :time AND WEEKDAY_ID = :day;'

        current_time = current_datetime.strftime("%H:%M")
        current_day = current_datetime.weekday()

        #Run command
        cur.execute(query, {'time': current_time, 'day': current_day})

        for item in cur.fetchall():
            print item

            heating_control(None, item['TYPE'], item['DEVICE_ID'], item['VALUE'], db, check_user=False)

def init_thread():
    while(True):
        run_heating_scheme()
        time.sleep(60)
    return