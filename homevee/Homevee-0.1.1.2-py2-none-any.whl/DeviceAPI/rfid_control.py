#!/usr/bin/python
# -*- coding: utf-8 -*-
from homevee.DeviceAPI.get_modes import get_modes
from homevee.DeviceAPI.set_modes import set_modes
from homevee.DeviceAPI.wake_on_lan import wake_on_lan
from homevee.Manager.dashboard import get_device_info
from homevee.device_types import *


def get_rfid_tags(username, db):
    with db:
        cur = db.cursor()

        cur.execute("SELECT * FROM RFID_TAGS")

        tags = []

        for item in cur.fetchall():
            try:
                device_info = get_device_info(username, item['ACTION_TYPE'], item['ACTION_ID'], db)

                print item
                print device_info

                tag = {'name': item['NAME'], 'uuid': item['UUID'], 'actiontype': item['ACTION_TYPE'],
                       'actionid': item['ACTION_ID'], 'roomname': device_info['roomname'], 'actionname': device_info['name']}
                tags.append(tag)
            except:
                continue

        return tags

def add_edit_rfid_tag(username, name, uuid, actionType, actionId, db):
    with db:
        cur = db.cursor()

        cur.execute("SELECT COUNT(*) FROM RFID_TAGS WHERE UUID = :uuid", {'uuid': uuid})

        is_new = cur.fetchone()['COUNT(*)'] is not 1

        param_array = {'name': name, 'uuid': uuid, 'type': actionType, 'id': actionId}

        if is_new:
            cur.execute("INSERT INTO RFID_TAGS (NAME, UUID, ACTION_TYPE, ACTION_ID) VALUES (:name, :uuid, :type, :id)",
                        param_array)
        else:
            cur.execute("UPDATE RFID_TAGS SET NAME = :name, ACTION_TYPE = :type, ACTION_ID = :id WHERE UUID = :uuid",
                        param_array)


    return {'result': 'ok'}

def delete_rfid_tag(userane, uuid, db):
    with db:
        cur = db.cursor()

        cur.execue("DELETE FROM RFID_TAGS WHERE UUID = :uuid", {'uuid': uuid})

    return {'result': 'ok'}


def wake_xbob_on_lan(username, id, db):
    pass


def run_rfid_action(username, uuid, db):
    with db:
        cur = db.cursor()

        cur.execute("SELECT * FROM RFID_TAGS WHERE UUID = :uuid", {'uuid': uuid})

        result = cur.fetchone()

        if result is None:
            return {'result': 'tagnotfound'}
        else:
            type = result['ACTION_TYPE']
            id = result['ACTION_ID']

            if type in [FUNKSTECKDOSE, ZWAVE_SWITCH, URL_SWITCH, URL_TOGGLE]:
                mode = get_modes(username, None, type, id, db)

                if mode == "1" or mode == 1 or mode == True or mode == "true":
                    mode = 0
                else:
                    mode = 1

                result = set_modes(username, type, id, mode, db)

            elif type == WAKE_ON_LAN:
                result = wake_on_lan(username, id, db)

            elif type == XBOX_ONE_WOL:
                result = wake_xbob_on_lan(username, id, db)

    return {'result': 'ok'}