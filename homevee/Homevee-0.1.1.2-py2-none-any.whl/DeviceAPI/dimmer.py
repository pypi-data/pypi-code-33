#!/usr/bin/python
# -*- coding: utf-8 -*-
from homevee.DeviceAPI import zwave
from homevee.Helper.helper_functions import has_permission
from homevee.device_types import *

def get_dimmers(username, room, db):
    if not has_permission(username, room, db):
        return {'status': 'nopermission'}

    dimmer = []

    with db:
        cur = db.cursor()

        #Z-Wave Dimmer
        cur.execute("SELECT * FROM ZWAVE_DIMMER WHERE LOCATION == :room", {'room': room})
        for item in cur.fetchall():
            dimmer_item = {'device': item['ID'], 'value': item['VALUE'], 'icon': item['ICON'],
                         'name': item['NAME'], 'type': ZWAVE_DIMMER}
            dimmer.append(dimmer_item)

        cur.close()

        return {'dimmer': dimmer}

def set_dimmer(username, type, id, value, db):
    if type == ZWAVE_DIMMER:
        return set_zwave_dimmer(username, id, value, db)
    else:
        raise ValueError("Type does not exist")

def set_zwave_dimmer(username, id, value, db):
    with db:
        cur = db.cursor()
        cur.execute("SELECT * FROM ZWAVE_DIMMER WHERE ID == :device",
                    {'device': id})

        data = cur.fetchone()

        if not has_permission(username, data['LOCATION'], db):
            return {'result': 'nopermission'}

        device_id = data['ID']

        result = zwave.device_control.set_multistate_device(device_id, value, db)

        if result['code'] == 200:
            cur.execute("UPDATE ZWAVE_DIMMER SET VALUE = :value WHERE ID = :id",
                        {'value': value, 'id': id})

            return {'result':'ok'}