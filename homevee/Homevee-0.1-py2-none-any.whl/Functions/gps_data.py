#!/usr/bin/python
# -*- coding: utf-8 -*-
from math import radians, cos, sqrt, atan2, sin

MIN_RETENTION_PERIOD = 5 * 60 * 1000 #5 minuten
MAX_DISTANCE = 500 #500 Meter

def update_gps(username, time, lat, lng, db):
    with db:
        cur = db.cursor()

        on_location_change(username, long(time), float(lat), float(lng), db)

        cur.execute("INSERT INTO GPS_DATA (USERNAME, TIMESTAMP, LATITUDE, LONGITUDE) VALUES (:user, :time, :lat, :lng);",
                    {'user': username, 'time': time, 'lat': lat, 'lng': lng})

        return {'result': 'ok'}

def on_location_change(username, time, lat, lng, db):
    #determine user location (at work, at school, at home, etc.)
    current_user_location = determine_user_location(username, time, lat, lng, db)
    set_user_location(username, current_user_location, db)

    return

def determine_user_location(username, time, lat, lng, db):
    #if user is longer than MIN_RETENTION_PERIOD in roughly the same place => update his location status
    #check distance to place => less than MAX_DISTANCE => user is there

    with db:
        cur = db.cursor()

        place = get_nearest_place(username, lat, lng, db)

        cur.execute("SELECT * FROM GPS_DATA WHERE USERNAME = :user ORDER BY TIMESTAMP DESC LIMIT 50", {'user': username})
        location_data = cur.fetchall()
        if place is not None and place['DISTANCE'] <= MAX_DISTANCE:
            for location in location_data:
                if(compute_distance(place['LATITUDE'], place['LONGITUDE'], location['LATITUDE'], location['LONGITUDE']) <= MAX_DISTANCE):
                    if(time - long(location['TIMESTAMP']) >= MIN_RETENTION_PERIOD):
                        return place
                else:
                    break

        return None

def get_nearest_place(username, lat, lng, db):
    with db:
        cur = db.cursor()

        cur.execute("SELECT *, ((LATITUDE - :lat)*(LATITUDE - :lat)) + ((LONGITUDE - :lng)*(LONGITUDE - :lng)) as DISTANCE FROM PLACES ORDER BY DISTANCE ASC LIMIT 1",
                    {'lat': lat, 'lng': lng})

        place = cur.fetchone()

        return place

def compute_distance(lat1, lng1, lat2, lng2):
    R = 6373000.0

    lat1 = radians(float(lat1))
    lng1 = radians(float(lng1))
    lat2 = radians(float(lat2))
    lng2 = radians(float(lng2))

    dlon = lng2 - lng1
    dlat = lat2 - lat1

    a = sin(dlat / 2) ** 2 + cos(lat1) * cos(lat2) * sin(dlon / 2) ** 2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))

    distance = R * c

    return distance

def set_user_location(username, place, db):
    with db:
        cur = db.cursor()

        place_id = -1

        if(place is not None):
            place_id = place['ID']

        cur.execute("UPDATE USERDATA SET CURRENT_LOCATION = :loc WHERE USERNAME = :user",
                    {'loc': place_id, 'user': username})

def get_gps_locations(username, db):
    with db:
        cur = db.cursor()

        locations = []

        cur.execute("SELECT * FROM GPS_DATA WHERE USERNAME = :user", {'user': username})

        for item in cur.fetchall():
            if not is_near(locations, item['LATITUDE'], item['LONGITUDE']):
                locations.append({'time': item['TIMESTAMP'], 'latitude': item['LATITUDE'], 'longitude': item['LONGITUDE']})

        return {'locations': locations}

def is_near(locations, lat, lng):
    MIN_DISTANCE_TO_OTHERS = 1000

    for location in locations:
        if (compute_distance(location['latitude'], location['longitude'], lat, lng) < MIN_DISTANCE_TO_OTHERS):
            return True
    return False