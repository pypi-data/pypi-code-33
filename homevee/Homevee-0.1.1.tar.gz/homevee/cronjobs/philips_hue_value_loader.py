#!/usr/bin/python
# -*- coding: utf-8 -*-
from time import sleep

from homevee.DeviceAPI import philips_hue
from homevee.db_utils import get_database_con


def load_hue_values(db):
    with db:
        cur = db.cursor()
        cur.execute("SELECT * FROM PHILIPS_HUE_LIGHTS")
        for item in cur.fetchall():
            counter = 3
            for i in range(0, counter):
                if(philips_hue.get_light_info(item['ID'], db)):
                    break



def init_thread():
    while True:
        db = get_database_con()
        load_hue_values(db)
        db.close()
        sleep(5*60)