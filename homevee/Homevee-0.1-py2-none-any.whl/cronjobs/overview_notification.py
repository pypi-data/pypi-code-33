#!/usr/bin/python
# -*- coding: utf-8 -*-
import datetime
from time import sleep

from homevee.Functions.calendar import get_calendar_day_items
from homevee.Functions.weather import get_weather
from homevee.db_utils import get_database_con
from homevee.firebase_utils import send_notification_to_users


def send_overview_notifications():
    db = get_database_con()

    with db:
        cur = db.cursor()

        cur.execute("SELECT * FROM USERDATA")

        users = cur.fetchall()

        for user in users:
            day_overview = ""

            weather = get_weather(1, db)
            weather_text = "Wetter: " + weather[0]['desc'] + ", " + str(weather[0]['temps']['min']) + "°C - " + str(weather[0]['temps']['max']) + "°C"

            today = datetime.datetime.today()
            date_today = today.strftime("%Y-%m-%d")
            calendar = get_calendar_day_items(user['USERNAME'], date_today, db)
            calendar_items = calendar['calendar_entries']
            if len(calendar_items) == 0:
                calendar_text = "Keine Termine"
            else:
                if len(calendar_items) > 1:
                    calendar_text = str(len(calendar_items)) + " Termine: "
                    for i in range(0, len(calendar_items)):
                        if i == 0:
                            calendar_text += calendar_items[i]['name'] + " um " + calendar_items[i]['start'] + " Uhr"
                        else:
                            calendar_text += ", " + calendar_items[i]['name'] + " um " + calendar_items[i]['start'] + " Uhr"
                else:
                    calendar_text = "Ein Termin: "+calendar_items[0]['name']+" um "+calendar_items[0]['start']+" Uhr"

            day_overview = weather_text+"\n"+calendar_text

            send_notification_to_users([user['USERNAME']], "Deine Tagesübersicht", day_overview, db)


def init_thread():
    while(True):
        #wait until midnight + 5 minutes
        t = datetime.datetime.today()

        seconds_to_wait = (24-t.hour)*60*60 - ((t.minute * 60) - t.second) + 5*60 #Warten bis 00:05
        #print "warten für benachrichtigung: " + str(seconds_to_wait) + " sekunden"


        #print "waiting until: "+ str(datetime.datetime.now() + datetime.timedelta(seconds=seconds_to_wait))

        #print "waiting for: "+str(seconds_to_wait)

        sleep(seconds_to_wait)

        send_overview_notifications()