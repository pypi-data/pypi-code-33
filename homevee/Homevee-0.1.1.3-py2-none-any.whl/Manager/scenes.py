#!/usr/bin/python
# -*- coding: utf-8 -*-
import json

from homevee.Helper.helper_functions import has_permission

def get_all_scenes(username, db):
    with db:
        cur = db.cursor()

        cur.execute("SELECT * FROM ROOMS")

        rooms = []

        for room in cur.fetchall():
            if not has_permission(username, room['LOCATION'], db):
                continue

            scenes = get_scenes(username, room['LOCATION'], db)

            scenes = scenes['scenes']

            if(len(scenes) is not 0):
                room_item = {'name': room['NAME'], 'location': room['LOCATION'], 'icon': room['ICON'], 'scenes': scenes}
                rooms.append(room_item)

        return {'rooms': rooms}

def get_scenes(username, location, db):
    scenes = []

    if has_permission(username, location, db):
        with db:
            cur = db.cursor()

            cur.execute("SELECT * FROM SCENES WHERE ROOM = :location",{'location': location})

            for item in cur.fetchall():
                scenes.append({'id': item['ID'], 'name': item['NAME'], 'action_data': item['ACTION_DATA'],
                              'location': item['ROOM']})

    return {'scenes': scenes}

def add_edit_scene(username, id, name, location, action_data, db):
    add_new = (id == None or id == "" or id == "-1")

    with db:
        cur = db.cursor()

        if(add_new):
            cur.execute("INSERT INTO SCENES (NAME, ROOM, ACTION_DATA) VALUES (:name, :room, :actions)",
                        {'name': name, 'room': location, 'actions': action_data})

            return {'result': 'ok'}

        else:
            cur.execute("UPDATE SCENES SET NAME = :name, ROOM = :location, ACTION_DATA = :actions WHERE ID = :id",
                {'name': name, 'location': location, 'actions': action_data, 'id': id})

            return {'result': 'ok'}

def delete_scene(username, id, db):
    with db:
        cur = db.cursor()

        cur.execute("DELETE FROM SCENES WHERE ID = :id", {'id': id})

        return {'result': 'ok'}