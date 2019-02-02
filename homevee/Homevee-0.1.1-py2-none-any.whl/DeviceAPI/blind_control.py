#!/usr/bin/python
# -*- coding: utf-8 -*-
import traceback

from homevee.DeviceAPI import rademacher_homepilot
from homevee.Helper.helper_functions import has_permission
from homevee.device_types import *


def set_blinds(username, type, id, new_position, db, check_user=True):
    try:
        with db:
            cur = db.cursor()

            if type == RADEMACHER_BLIND_CONTROL:
                cur.execute("SELECT LOCATION FROM HOMEPILOT_BLIND_CONTROL WHERE ID = :id", {'id': id})
                data = cur.fetchone()
                if check_user and not has_permission(username, data['LOCATION'], db):
                    return {'result': 'nopermission'}

                return rademacher_homepilot.blinds_control.control_blinds(id, new_position, db)
            else:
                return {'result': 'nosuchtype'}
    except:
        traceback.print_exc()
        return {'result': 'error'}

    return {'result': 'ok'}

def set_room_blinds(username, room, new_position, db):
    with db:
        cur = db.cursor()
        devices = get_blinds(username, room, db)
        
        for device in devices['blinds']:
            id = device['id']
            type = device['type']
            result = set_blinds(username, type, id, new_position, db)
            if 'result' not in result or result['result'] != 'ok':
                return {'result': 'error'}
        return {'result': 'ok'}
        
def get_all_blinds(username, db):
    with db:
        cur = db.cursor()
        cur.execute("SELECT * FROM ROOMS")
        rooms = cur.fetchall()
        blinds = []
        for room in rooms:
            if not has_permission(username, room['LOCATION'], db):
                continue
            room_blinds = {'name': room['NAME'], 'location': room['LOCATION'], 'icon': room['ICON'],
                                'blind_array': get_blinds(username, room['LOCATION'], db)}
            blinds.append(room_blinds)
        return {'blinds': blinds}

def get_blinds(username, location, db):
    if not has_permission(username, location, db):
        return {'result': 'nopermission'}

    with db:
        blinds = []

        cur = db.cursor()

        #Rademacher HomePilot
        cur.execute("SELECT * FROM HOMEPILOT_BLIND_CONTROL WHERE LOCATION = :location",
                    {'location': location})
        for item in cur.fetchall():
            value = int(item['LAST_POS'])

            if value is None:
                value = 0

            blinds.append({'name': item['NAME'], 'id': item['ID'], 'location': location,
                           'icon': item['ICON'], 'value': value, 'type': RADEMACHER_BLIND_CONTROL})

        #Andere Gerätetypen

        return {'blinds': blinds}
