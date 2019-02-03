#!/usr/bin/python
# -*- coding: utf-8 -*-
import urllib2

from homevee.DeviceAPI import philips_hue
from homevee.Helper.helper_functions import has_permission
from homevee.device_types import *


def rgb_control(username, devicetype, id, mode, brightness, color, db, check_user=True):
    with db:
        cur = db.cursor()

        if devicetype == URL_RGB_LIGHT:
            cur.execute("SELECT * FROM URL_RGB_LIGHT WHERE ID = :id", {'id': id})

            result = cur.fetchone()

            if check_user and not has_permission(username, result['LOCATION'], db):
                return {'result': 'nopermission'}

            output = urllib2.urlopen("http://"+result['URL']+color).read()

            return {'result': 'ok'}
        elif devicetype == PHILIPS_HUE_LIGHT:
            return philips_hue.set_light_mode(username, id, mode, None, brightness, color, db, check_user=True)

def get_rgb_devices(username, room, db):
    if(not has_permission(username, room, db)):
        return {'result': 'nopermission'}

    devices = []

    with db:
        cur = db.cursor()

        #URL_RGB_LIGHT
        cur.execute("SELECT * FROM URL_RGB_LIGHT WHERE LOCATION = :room", {'room': room})
        for item in cur.fetchall():
            rgb_item = {'name': item['NAME'], 'id': item['ID'], 'type': URL_RGB_LIGHT,
            'icon': item['ICON'], 'value': {'is_on': False, 'brightness': 100, 'color': item['LAST_COLOR']}}
            devices.append(rgb_item)
        #PHILIPS_HUE
        cur.execute("SELECT * FROM PHILIPS_HUE_LIGHTS WHERE LOCATION = :room AND TYPE = 'color'", {'room': room})
        for item in cur.fetchall():
            rgb_item = {'name': item['NAME'], 'id': item['ID'], 'type': PHILIPS_HUE_LIGHT,
                        'icon': item['ICON'], 'value': {'is_on': item['IS_ON']== 1, 'brightness': int(item['BRIGHTNESS']/255*100), 'color': item['HUE']}}
            devices.append(rgb_item)

    return {'rgb': devices}

def get_rgb_device(username, type, id, db):
    with db:
        cur = db.cursor()

        #URL_RGB_LIGHT
        if type == URL_RGB_LIGHT:
            cur.execute("SELECT * FROM URL_RGB_LIGHT WHERE ID = :id", {'id': id})
            item = cur.fetchone()
            rgb_item = {'name': item['NAME'], 'id': item['ID'], 'type': URL_RGB_LIGHT,
            'icon': item['ICON'], 'value': {'is_on': False, 'brightness': 100, 'color': item['LAST_COLOR']}}
            return rgb_item
        #PHILIPS_HUE
        elif type == PHILIPS_HUE_LIGHT:
            cur.execute("SELECT * FROM PHILIPS_HUE_LIGHTS WHERE ID = :id AND TYPE = 'color'", {'id': id})
            item = cur.fetchone()
            rgb_item = {'name': item['NAME'], 'id': item['ID'], 'type': PHILIPS_HUE_LIGHT,
                        'icon': item['ICON'], 'value': {'is_on': item['IS_ON']== 1,
                        'brightness': int(item['BRIGHTNESS']/255*100), 'color': item['HUE']}}
            return rgb_item