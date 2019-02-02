#!/usr/bin/python
# -*- coding: utf-8 -*-
import datetime
import urllib2
from time import sleep

from homevee.Manager.api_key import get_api_key
from homevee.db_utils import get_server_data, get_database_con


def refresh_weather_cache(db):
    api_key = get_api_key("Open Weather Map", db)
    location_id = get_server_data("WEATHER_LOCATION_ID", db)

    url = "http://api.openweathermap.org/data/2.5/forecast/daily?id=" + location_id + "&cnt=16&units=metric&lang=de&type=accurate&APPID=" + api_key
    response = urllib2.urlopen(url).read()

    with db:
        cur = db.cursor()

        # Wetter-Daten in Datenbank schreiben
        cur.execute("INSERT OR REPLACE INTO SERVER_DATA (KEY, VALUE) values('WEATHER_CACHE', :response);",
                    {"response": response})
        db.commit()

def init_thread():
    while True:
        db = get_database_con()
        refresh_weather_cache(db)

        t = datetime.datetime.today()

        seconds_to_wait = (15 * 60) - ((t.minute * 60) - t.second)%15*60
        #print "warten für wetter: "+str(seconds_to_wait)+" sekunden"
        sleep(seconds_to_wait)