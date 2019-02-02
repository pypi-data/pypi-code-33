#!/usr/bin/python
# -*- coding: utf-8 -*-
from homevee.Functions.room_data import get_room_data
from homevee.Helper.helper_functions import has_permission
from homevee.Manager.scenes import get_scenes


def add_edit_room(username, room_name, room_key, icon, db):
    if not has_permission(username, "admin", db):
        return {'status': 'noadmin'}

    param_array = {'name': room_name, 'icon': icon}

    with db:
        cur = db.cursor()

        if room_key is not None and room_key != "":
            #print "edit room"
            param_array['location'] = room_key
            cur.execute("UPDATE ROOMS SET NAME = :name, ICON = :icon WHERE LOCATION == :location;",
                param_array)
        else:
            #print "add room"
            cur.execute("INSERT INTO ROOMS (NAME, ICON) VALUES (:name, :icon);",
                    param_array)

    return {'result': 'ok'}

def delete_room(username, room_key, db):
    if not has_permission(username, "admin", db):
        return {'status': 'noadmin'}

    roomdata = get_room_data(username, room_key, db)['roomdata']

    if len(roomdata) == 1:
        if roomdata[0]['type'] == "scenes":
            scenes = get_scenes(username, room_key, db)

            for scene in scenes['scenes']:
                if scene['room'] == room_key:
                    return "roomhasitems"
    elif len(roomdata) > 1:
        return "roomhasitems"

    with db:
        cur = db.cursor()

        cur.execute("DELETE FROM ROOMS WHERE LOCATION == :location",
                    {'location': room_key})

    return {'result': 'ok'}

def move_items_and_delete_old_room(username, old_room, new_room, db):
    if not has_permission(username, "admin", db):
        return {'status': 'noadmin'}

    params = {'oldroom': old_room, 'newroom': new_room}

    query_array = []

    #Funksteckdosen
    query_array.append("UPDATE 'funksteckdosen' SET ROOM = :newroom WHERE ROOM == :oldroom;")

    #Z-Wave
    query_array.append("UPDATE 'ZWAVE_SENSOREN' SET RAUM = :newroom WHERE RAUM == :oldroom;")
    query_array.append("UPDATE 'ZWAVE_THERMOSTATS' SET RAUM = :newroom WHERE RAUM == :oldroom;")

    #DIY
    query_array.append("UPDATE 'DIY_DEVICES' SET ROOM = :newroom WHERE ROOM == :oldroom;")
    query_array.append("UPDATE 'DIY_SENSORS' SET RAUM = :newroom WHERE RAUM == :oldroom;")
    query_array.append("UPDATE 'DIY_REEDSENSORS' SET RAUM = :newroom WHERE RAUM == :oldroom;")
    query_array.append("UPDATE 'DIY_SWITCHES' SET RAUM = :newroom WHERE RAUM == :oldroom;")

    #Szenen
    query_array.append("UPDATE 'SCENES' SET ROOM = :newroom WHERE ROOM == :oldroom;")

    with db:
        cur = db.cursor()
        for query in query_array:
            cur.execute(query, params)

    return delete_room(username, old_room, db)

def delete_room_with_items(username, room_key, db):
    if not has_permission(username, "admin", db):
        return {'status': 'noadmin'}

    params = {'oldroom': room_key}

    query_array = []

    # Funksteckdosen
    query_array.append("DELETE FROM 'funksteckdosen' WHERE ROOM == :oldroom;")

    # Z-Wave
    query_array.append("DELETE FROM 'ZWAVE_SENSOREN' WHERE RAUM == :oldroom;")
    query_array.append("DELETE FROM 'ZWAVE_THERMOSTATS' WHERE RAUM == :oldroom;")

    # DIY
    query_array.append("DELETE FROM 'DIY_DEVICES' WHERE ROOM == :oldroom;")
    query_array.append("DELETE FROM 'DIY_REEDSENSORS' WHERE RAUM == :oldroom;")
    query_array.append("DELETE FROM 'DIY_SENSORS' WHERE RAUM == :oldroom;")
    query_array.append("DELETE FROM 'DIY_SWITCHES' WHERE RAUM == :oldroom;")

    # Szenen
    query_array.append("DELETE FROM 'SCENES' WHERE ROOM == :oldroom;")

    with db:
        cur = db.cursor()
        for query in query_array:
            cur.execute(query, params)

    return delete_room(username, room_key, db)