#!/usr/bin/python
# -*- coding: utf-8 -*-

import json
import datetime

'''Gibt das Wetter für die angegebene Anzahl an Tagen zurück'''
def get_weather(daycount, db):
    if daycount > 16:
        daycount = 16

    with db:
        cur = db.cursor()

        cur.execute("SELECT VALUE FROM SERVER_DATA WHERE KEY = 'WEATHER_CACHE'")

        data = cur.fetchone()

        weather_data = json.loads(data['VALUE'])

        days = weather_data['list']

        output = []

        for i in range(0, min(days, daycount)):
            day = days[i]

            relative_days = ["Heute", "Morgen", "Übermorgen"]
            day_names = ["Mo", "Di", "Mi", "Do", "Fr", "Sa", "So"]

            if i > 2:
                date = datetime.datetime.fromtimestamp(day['dt'])

                week_day_number = date.weekday()

                date = day_names[week_day_number]+", "+date.strftime('%d.%m.')
            else:
                date = relative_days[i]

            city_name = weather_data['city']['name']

            icon_link = "http://openweathermap.org/img/w/"+day['weather'][0]['icon']+".png"

            weather_desc = day['weather'][0]['description']
            icon = day['weather'][0]['icon']

            pressure = None
            if "pressure" in day:
                pressure = day['pressure']

            humidity = None
            if "humidity" in day:
                humidity = day['humidity']

            wind_speed = None
            if "speed" in day:
                wind_speed = float(day['speed'])*3.6

            wind_direction = None
            if "deg" in day:
                wind_direction = day['deg']

            clouds = None
            if "clouds" in day:
                clouds = day['clouds']

            rain = None
            if "rain" in day:
                rain = day['rain']

            snow = None
            if "snow" in day:
                snow = day['snow']

            day_item = {'city':city_name, 'date':date, 'temps':day['temp'], 'icon':icon_link, 'iconid':icon,
                        'desc':weather_desc, 'pressure':pressure, 'humidity':humidity, 'windspeed':wind_speed,
                        'winddirection': wind_direction, 'clouds':clouds, 'rain':rain, 'snow':snow}

            output.append(day_item)

        cur.close()

        return output

'''Setzt die Orts-ID zur Wetter-Abfrage'''
def set_weather_city_id(request, db):
    return

'''Gibt alle Orte zur Wetterabfrage zurück'''
def get_weather_city_list(db):
    with db:
        cur = db.cursor()
        cur.execute("SELECT VALUE FROM SERVER_DATA WHERE KEY = 'WEATHER_CITY_CACHE'")
        cities = cur.fetchone()['VALUE']

        cur.close()

        return cities