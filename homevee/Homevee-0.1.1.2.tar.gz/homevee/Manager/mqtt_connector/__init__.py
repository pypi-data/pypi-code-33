#!/usr/bin/python
# -*- coding: utf-8 -*-
import json

from homevee.Helper.helper_functions import has_permission, get_my_ip
from homevee.db_utils import get_server_data


def generate_key():
    return "123456"

def save_mqtt_device(username, type, location, id, data, db):
    if not has_permission(username, location, db):
        return {'result': 'nopermission'}

    with db:
        cur = db.cursor()

        #if type == MQTT_SENSOR:
        #    cur.execute("INSERT INTO MQTT_SENSORS")
            
        item_data = json.loads(data)
        
        for item in item_data:
            if item['devicetype'] == "sensor":
                cur.execute("INSERT INTO MQTT_SENSORS (NAME, ICON, TYPE, ROOM, SAVE_DATA, DEVICE_ID, VALUE_ID, LAST_VALUE) VALUES (:name, :icon, :type, :room, :save_data, :dev_id, :val_id, \"N/A\")",
                {'name': item['name'], 'icon': item['icon'], 'type': item['sensor_type'],
                'room': location, 'save_data': item['save_data'], 'dev_id': id, 'val_id': item['id']})
        
    return {'result': 'ok'}

def generate_device_data(username, location, db):
    if not has_permission(username, location, db):
        return {'result': 'nopermission'}

    with db:
        cur = db.cursor()

        cur.execute("SELECT * FROM MQTT_DEVICES ORDER BY ID DESC")

        item = cur.fetchone()

        if item is not None:
            new_id = item['ID']+1
        else:
            new_id = 0

        topic = "/home/device/"+str(new_id)

        key = generate_key()

        cur.execute("INSERT INTO MQTT_DEVICES (ID, LOCATION, KEY, TOPIC) VALUES (:id, :location, :key, :topic)",
                    {'id': new_id, 'location': location, 'key': key, 'topic': topic})

        return {'id': new_id, 'topic': topic, 'key': key, 'ip': get_my_ip(),
                'remoteid': get_server_data("REMOTE_ID", db)}

def add_to_intermediates(id, db):
    with db:
        cur = db.cursor()

        cur.execute("INSERT INTO MQTT_DEVICE_INTERMEDIATES (ID) VALUES (:id)",
                    {'id': id})

def is_in_intermediates(id, db):
    with db:
        cur = db.cursor()

        cur.execute("SELECT COUNT(*) FROM MQTT_DEVICE_INTERMEDIATES WHERE ID = :id",
                    {'id': id})

        data = cur.fetchone()

        if data['COUNT(*)'] == 0:
            return False
        else:
            return True
