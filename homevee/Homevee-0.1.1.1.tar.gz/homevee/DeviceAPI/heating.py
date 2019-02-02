#!/usr/bin/python
# -*- coding: utf-8 -*-
import traceback

from homevee.DeviceAPI import rademacher_homepilot
from homevee.DeviceAPI.max_cube import set_temp
from homevee.DeviceAPI.zwave.get_devices import get_device_value, set_device_value
from homevee.DeviceAPI.zwave.utils import do_zwave_request
from homevee.Helper.helper_functions import has_permission
from homevee.device_types import *

def heating_control(username, type, id, value, db, check_user=True):
    try:
        with db:
            cur = db.cursor()

            if type == ZWAVE_THERMOSTAT:
                cur.execute("SELECT RAUM FROM ZWAVE_THERMOSTATS WHERE THERMOSTAT_ID = :id", {'id': id})
                data = cur.fetchone()
                if check_user and not has_permission(username, data['RAUM'], db):
                    return {'result': 'nopermission'}

                #update value in db as well
                set_device_value(type, id, value, db)

                result = do_zwave_request("/ZAutomation/api/v1/devices/"+str(id)+"/command/exact?level="+str(value), db)

                if result['code'] == 200:
                    return {'result': 'ok'}
                else:
                    return {'result': 'error'}
            elif type == MAX_THERMOSTAT:
                cur.execute("SELECT RAUM FROM MAX_THERMOSTATS WHERE ID = :id", {'id': id})
                data = cur.fetchone()
                if check_user and not has_permission(username, data['RAUM'], db):
                    return {'result': 'nopermission'}

                return set_temp(id, value, db)
            elif type == RADEMACHER_THERMOSTAT:
                cur.execute("SELECT ROOM FROM HOMEPILOT_THERMOSTATS WHERE ID = :id", {'id': id})
                data = cur.fetchone()
                if check_user and not has_permission(username, data['ROOM'], db):
                    return {'result': 'nopermission'}

                return rademacher_homepilot.heating_control.heating_control(id, value, db)
            else:
                return {'result': 'nosuchtype'}
    except:
        traceback.print_exc()
        return {'result': 'error'}

def control_room_heating(username, room, value, db):
    with db:
        devices = get_thermostats(username, room, "", "", db)['thermostats'][0]['thermostat_array']
        for device in devices:
            id = device['id']
            type = device['type']
            result = heating_control(username, type, id, value, db)
            if 'result' not in result or result['result'] != "ok":
                return {'result': 'error'}
        return {'result': 'ok'}

def get_thermostats(username, room, type, id, db):
    with db:
        cur = db.cursor()

        if type != "" and id != "":
            #if not has_permission(username, room, db):
            #   return {'result': 'nopermission'}

            if type == ZWAVE_THERMOSTAT:
                '''
                cur.execute("SELECT RAUM FROM ZWAVE_THERMOSTATS WHERE THERMOSTAT_ID = :id", {'id': id})
                data = cur.fetchone()
                if not has_permission(username, data['RAUM'], db):
                    return {'result': 'nopermission'}

                result = do_zwave_request("/ZAutomation/api/v1/devices/"+id, db)

                if result['code'] != 200:
                    return "N/A"

                return {'value': result['data']['metrics']['level'],
                        'min': result['data']['metrics']['min'],
                        'max': result['data']['metrics']['max']}
                '''

                value = get_device_value(type, id, db)
                return {'value': value, 'min': 4, 'max': 40}

            elif type == MAX_THERMOSTAT:
                cur.execute("SELECT * FROM MAX_THERMOSTATS WHERE ID == :id",
                            {'id': id})

                result = cur.fetchone()

                return {'value': result['LAST_TEMP'], 'min': 0, 'max': 30}

            elif type == RADEMACHER_THERMOSTAT:
                cur.execute("SELECT * FROM HOMEPILOT_THERMOSTATS WHERE ID == :id",
                            {'id': id})

                result = cur.fetchone()

                return {'value': result['LAST_TEMP'], 'min': 4, 'max': 28}

            else:
                return {'result': 'nosuchtype'}
        else:
            if room == "all":
                cur.execute("SELECT * FROM ROOMS")
            else:
                cur.execute("SELECT * FROM ROOMS WHERE LOCATION == :room",
                            {'room': room})

            rooms = cur.fetchall()

            thermostats = []

            for room in rooms:
                if not has_permission(username, room['LOCATION'], db):
                    continue

                thermostat_array = []

                # Alle Z-Wave Thermostate des Raumes laden
                type = ZWAVE_THERMOSTAT
                cur.execute("SELECT * FROM ZWAVE_THERMOSTATS WHERE RAUM == :location",
                            {'location': room['LOCATION']})
                results = cur.fetchall()
                for result in results:
                    thermostat = {'name': result['NAME'], 'id': result['THERMOSTAT_ID'],
                                  'type': type, 'icon': result['ICON'],
                                  'data': get_thermostats(username, room['LOCATION'], type, result['THERMOSTAT_ID'], db)}
                    thermostat_array.append(thermostat)

                # Alle MAX! Thermostate des Raumes laden
                type = MAX_THERMOSTAT
                cur.execute("SELECT * FROM MAX_THERMOSTATS WHERE RAUM == :location",
                            {'location': room['LOCATION']})
                results = cur.fetchall()
                for result in results:
                    thermostat = {'name': result['NAME'], 'id': result['ID'],
                                  'type': type, 'icon': result['ICON'],
                                  'data': get_thermostats(username, room['LOCATION'], type, result['ID'], db)}
                    thermostat_array.append(thermostat)

                # Alle Rademacher Thermostate des Raumes laden
                type = RADEMACHER_THERMOSTAT
                cur.execute("SELECT * FROM HOMEPILOT_THERMOSTATS WHERE ROOM == :location",
                            {'location': room['LOCATION']})
                results = cur.fetchall()
                for result in results:
                    thermostat = {'name': result['NAME'], 'id': result['ID'],
                                  'type': type, 'icon': result['ICON'],
                                  'data': get_thermostats(username, room['LOCATION'], type, result['ID'], db)}
                    thermostat_array.append(thermostat)

                room_thermostats = {'name': room['NAME'], 'location': room['LOCATION'], 'icon': room['ICON'],
                                    'thermostat_array': thermostat_array}
                thermostats.append(room_thermostats)

            return {'thermostats': thermostats}
