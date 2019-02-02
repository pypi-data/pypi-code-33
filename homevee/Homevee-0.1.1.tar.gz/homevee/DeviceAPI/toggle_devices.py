#!/usr/bin/python
# -*- coding: utf-8 -*-

def get_toggle_devices(username, room, db):
    devices = []

    with db:
        cur = db.cursor()

        cur.execute("SELECT * FROM URL_TOGGLE WHERE LOCATION = :location",
                    {'location': room})

        for toggle in cur.fetchall():
            devices.append({'name': toggle['NAME'], 'id': toggle['ID'], 'type': 'URL-Toggle',
                'icon': toggle['ICON']})

    return {'toggles': devices}