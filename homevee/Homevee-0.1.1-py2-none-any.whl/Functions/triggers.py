#!/usr/bin/python
# -*- coding: utf-8 -*-
from homevee.Helper.helper_functions import has_permission


def add_trigger(username, location, id, db):
    return

def get_triggers(username, room, db):
    if not has_permission(username, room, db):
        return {'result': 'nopermission'}

    triggers = []

    with db:
        cur = db.cursor()

        cur.execute("SELECT * FROM MQTT_TRIGGERS WHERE LOCATION = :location", {'location': room})

        for item in cur.fetchall():
            triggers.append({'name': item['NAME'], 'id': item['ID'], 'type': 'MQTT-Trigger', 'icon': item['ICON']})

    return {'triggers': triggers}