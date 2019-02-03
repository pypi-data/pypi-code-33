#!/usr/bin/python
# -*- coding: utf-8 -*-
from homevee.DeviceAPI.rgb_control import rgb_control
from homevee.VoiceAssistant.helper import find_room
from homevee.VoiceAssistant.voice_patterns import PATTERN_RGB_CONTROL
from homevee.colors import COLORS, COLOR_NAMES
from homevee.device_types import *

def get_pattern(db):
    return PATTERN_RGB_CONTROL

def get_label():
    return "rgb"

def run_command(username, text, context, db):
    return voice_rgb_control(username, text, context, db)

def voice_rgb_control(username, text, context, db):
    room = find_room(text, db)

    if room is not None:
        room_key = room['LOCATION']
    else:
        room_key = None

    devices = find_devices(text, room_key, db)

    color = find_color(text)
    if color != False:
        color_hex = COLOR_NAMES[color]
    else:
        return "Du musst mir eine Farbe sagen."

    for device in devices:
        rgb_control(username, device['type'], device['id'], True, None, color_hex, db)

        return {'msg_speech': 'Ok.', 'msg_text': 'Ok.'}

def find_devices(text, location_key, db):
    devices = []

    with db:
        cur = db.cursor()

        #data => table_name, name_key, id_key, type_key, location_key
        data = [
            ['PHILIPS_HUE_LIGHTS','NAME','ID',PHILIPS_HUE_LIGHT,'LOCATION'],
            ['URL_RGB_LIGHT','NAME','ID',URL_RGB_LIGHT,'LOCATION']
        ]

        for item in data:
            if location_key is None:
                cur.execute("SELECT * FROM "+item[0])
            else:
                param_array = {'location': location_key}
                cur.execute("SELECT * FROM "+item[0]+" WHERE "+item[4]+" = :location", param_array)

            for device in cur.fetchall():
                position = text.find(device[item[1]].lower())
                if position is not -1:
                    device_item = {'type': item[3], 'name': device[item[1]], 'id': device[item[2]]}
                    devices.append(device_item)

    return devices

def find_color(text):
    for word in text.split():
        for color in COLORS:
            if word == color:
                return color

    return False