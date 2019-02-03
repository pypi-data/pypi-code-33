#!/usr/bin/python
# -*- coding: utf-8 -*-
from homevee.DeviceAPI.wake_on_lan import wake_on_lan
from homevee.VoiceAssistant import context_keys
from homevee.VoiceAssistant.helper import generate_string, set_context, find_room, get_okay
from homevee.device_types import *


def voice_wol(username, text, context, db):
    room = find_room(text, db)

    if room is not None:
        room_key = room['LOCATION']
    else:
        room_key = None

    devices = find_devices(text, room_key, db)

    if len(devices) == 0:
        #Keine Geräte gefunden
        answer_data = [
            [['Dieses ', 'Das genannte '], 'Gerät ', ['existiert nicht.', 'gibt es nicht.', 'wurde noch nicht angelegt.']]
        ]

        answer = generate_string(answer_data)

        return {'msg_speech': answer, 'msg_text': answer}

    words = text.split(" ")

    #Geräte schalten
    for device in devices:
        if device['type'] == XBOX_ONE_WOL:
            print ""
            #xbox_wake_up(username, device['id'], db)
        else:
            wake_on_lan(username, device['id'], db)

    set_context(username, context_keys.WOL, {'location': room, 'devices': devices}, db)

    DEVICE_STRING = None
    if len(devices) > 1:
        VERB = "wurden"
        DEVICE_WORD = "Die Geräte "

        for i in range(0, len(devices)):
            if DEVICE_STRING is None:
                DEVICE_STRING = '\'' + devices[i]['name'] + '\''
            elif i == len(devices) - 1:
                DEVICE_STRING = DEVICE_STRING + ' und ' + '\'' + devices[i]['name'] + '\''
            else:
                DEVICE_STRING = DEVICE_STRING + ', ' + '\'' + devices[i]['name'] + '\''
    else:
        DEVICE_WORD = "Das Gerät "
        VERB = "wurde"

        DEVICE_STRING = '\'' + devices[0]['name'] + '\''

    answer_data = [
        [get_okay(), [', ' + username, ''], '.',
         ['', [' ', DEVICE_WORD,  [DEVICE_STRING + ' ', ''], VERB + ' ',
               ['gestartet', 'eingeschalten', 'eingeschaltet', 'an gemacht', 'hochgefahren'], '.']]]
    ]

    answer = generate_string(answer_data)

    return {'msg_speech': answer, 'msg_text': answer}

def find_devices(text, location_key, db):
    devices = []

    with db:
        cur = db.cursor()

        #data => table_name, name_key, id_key, type_key, location_key
        data = [
            ['WAKE_ON_LAN','NAME','DEVICE', WAKE_ON_LAN,'LOCATION'],
            ['XBOX_ONE_WOL','NAME','ID', XBOX_ONE_WOL,'LOCATION']
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