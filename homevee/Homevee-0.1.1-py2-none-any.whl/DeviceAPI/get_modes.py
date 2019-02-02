#!/usr/bin/python
# -*- coding: utf-8 -*-

from homevee.DeviceAPI.zwave.get_devices import get_device_value
from homevee.device_types import *
from homevee.Helper.helper_functions import has_permission


def get_modes(username, room, type, id, db):
    if not has_permission(username, room, db):
        return {'status': 'nopermission'}

    if id == "":
        modi = []

        with db:
            cur = db.cursor()

            #Funksteckdosen laden
            cur.execute("SELECT * FROM FUNKSTECKDOSEN WHERE ROOM == :room", {'room': room})
            for item in cur.fetchall():
                mode_item = {'device': item['DEVICE'], 'mode': item['ZUSTAND'], 'icon': item['ICON'],
                    'name': item['NAME'], 'type': FUNKSTECKDOSE}
                modi.append(mode_item)

            #Z-Wave Schalter
            cur.execute("SELECT * FROM ZWAVE_SWITCHES WHERE LOCATION == :room", {'room': room})
            for item in cur.fetchall():
                mode_item = {'device': item['ID'], 'mode': get_modes(username, room, "Z-Wave Schalter", item['ID'], db), 'icon': item['ICON'],
                             'name': item['NAME'], 'type': ZWAVE_SWITCH}
                modi.append(mode_item)

            cur.close()

            return {'modi': modi}
    else:
        with db:
            cur = db.cursor()

            if type == FUNKSTECKDOSE:
                cur.execute("SELECT * FROM FUNKSTECKDOSEN WHERE DEVICE == :device", {'device': id})
                return cur.fetchone()['ZUSTAND']
            elif type == ZWAVE_SWITCH:
                '''gateway_data = get_gateway("Z-Wave", db)

                port = ""

                if gateway_data['PORT'] is not None and gateway_data['PORT'] != "":
                    port = ":"+gateway_data['IP'];

                link = "http://"+gateway_data['IP']+port+"/ZAutomation/api/v1/devices/"+id

                result = "{}"

                array = json.loads(result)

                if "code" not in array or array['code'] != "200":
                    return "false"

                return str(array['data']['metrics']['level'] == "on")'''
                return get_device_value(ZWAVE_SWITCH, id, db)