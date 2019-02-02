#!/usr/bin/python
# -*- coding: utf-8 -*-
from homevee.device_types import *
from homevee.DeviceAPI.zwave.device_control import get_data
from homevee.DeviceAPI.zwave.utils import do_zwave_request


def get_devices(db):
    json_data = do_zwave_request("/ZAutomation/api/v1/locations", db)

    room_data = json_data['data']

    devices = []

    for room in room_data:
        room_id = room['id']
        room_title = room['title']

        for namespace in room['namespaces']:
            if namespace['id'] == 'devices_all':
                for device in namespace['params']:
                    item_data = get_data(device['deviceId'], db)['data']

                    if 'deviceType' in item_data:
                        device_type = item_data['deviceType']

                    device_item = {'title': device['deviceName'], 'id': device['deviceId'],
                                   'room': room_title, 'type': device_type}
                    devices.append(device_item)

    if json_data['code'] == 200:
        return {'devices': devices}
    else:
        return "error"

def get_device_value(type, id, db):
    data = {
        ZWAVE_SENSOR: {'table': 'ZWAVE_SENSOREN', 'id_col': 'ID', 'val_col': 'VALUE'},
        ZWAVE_POWER_METER: {'table': 'ZWAVE_POWER_METER', 'id_col': 'DEVICE_ID', 'val_col': 'VALUE'},
        ZWAVE_THERMOSTAT: {'table': 'ZWAVE_THERMOSTATS', 'id_col': 'THERMOSTAT_ID', 'val_col': 'VALUE'},
        ZWAVE_SWITCH: {'table': 'ZWAVE_SWITCHES', 'id_col': 'ID', 'val_col': 'VALUE'},
        ZWAVE_DIMMER: {'table': 'ZWAVE_DIMMER', 'id_col': 'ID', 'val_col': 'VALUE'}
    }

    if type in data:
        with db:
            cur = db.cursor()

            cur.execute('SELECT * FROM '+data[type]['table']+' WHERE '+data[type]['id_col']+' = :id',
                        {'id': id})

            result = cur.fetchone()

            #print type+" - "+id

            return result[data[type]['val_col']]
    else:
        return None

def set_device_value(type, id, value, db):
    data = {
        ZWAVE_SENSOR: {'table': 'ZWAVE_SENSOREN', 'id_col': 'ID', 'val_col': 'VALUE'},
        ZWAVE_POWER_METER: {'table': 'ZWAVE_POWER_METER', 'id_col': 'DEVICE_ID', 'val_col': 'VALUE'},
        ZWAVE_THERMOSTAT: {'table': 'ZWAVE_THERMOSTATS', 'id_col': 'THERMOSTAT_ID', 'val_col': 'VALUE'},
        ZWAVE_SWITCH: {'table': 'ZWAVE_SWITCHES', 'id_col': 'ID', 'val_col': 'VALUE'},
        ZWAVE_SWITCH: {'table': 'ZWAVE_DIMMER', 'id_col': 'ID', 'val_col': 'VALUE'}
    }

    if type in data:
        with db:
            #print "Saving: "+type+" - "+id+" - "+str(value)

            cur = db.cursor()

            if type == ZWAVE_POWER_METER:
                cur.execute("SELECT * FROM ZWAVE_POWER_METER WHERE DEVICE_ID = :id", {'id': id})
                result = cur.fetchone()

                try:
                    prev_value = float(result['PREV_VALUE'])
                    if result['IS_RESET_DAILY']==0 and value < prev_value:
                        cur.execute("UPDATE ZWAVE_POWER_METER SET PREV_VALUE = 0 WHERE DEVICE_ID = :id",
                                    {'id': id})
                    else:
                        value = value - prev_value
                except:
                    value = value

            cur.execute('UPDATE '+data[type]['table']+' SET '+data[type]['val_col']+' = :value WHERE '+data[type]['id_col']+' = :id',
                        {'value': value, 'id': id})

            return True
    else:
        return False