#!/usr/bin/python
# -*- coding: utf-8 -*-
import json

import requests

from homevee.Helper.helper_functions import has_permission
from homevee.Manager.gateway import get_gateway
from homevee.gateway_keys import PHILIPS_HUE


def set_light_mode(username, id, mode, saturation, brightness, color, db, check_user=True):
    with db:
        cur = db.cursor()

        cur.execute("SELECT LOCATION FROM PHILIPS_HUE_LIGHTS WHERE ID = :id", {'id': id})

        result = cur.fetchone()

        if result is None:
            return {'result': 'error'}
        elif check_user and not has_permission(username, result['LOCATION'], db):
            return {'result': 'nopermission'}

        data = get_gateway(PHILIPS_HUE, db)
        ip = data['IP']
        user = data['KEY1']

        if mode == True or mode == "1":
            mode = True
        else:
            mode = False

        data = {}

        cur.execute("SELECT * FROM PHILIPS_HUE_LIGHTS WHERE ID = :id", {'id': id})

        result = cur.fetchone()

        if color is not None:
            rgb = tuple(int(color[i:i + 2], 16) for i in (0, 2, 4))
            x, y, z = rgb_to_xy(rgb)
            data['xy'] = [x, y]
            data['sat'] = int(z*255)
        else:
            data['hue'] = result['HUE']

        if mode is not None:
            data['on'] = mode
        else:
            data['on'] = result['IS_ON'] == 1

        if brightness is not None:
            data['bri'] = int(float(brightness)*255/100)
        else:
            data['bri'] = int(result['BRIGHTNESS'])

        print "rgb"

        response = requests.put("http://" + ip + "/api/" + user + "/lights/" + str(id) + "/state", data=json.dumps(data))

        print response.text

        update_light_info(id, mode, color, saturation, brightness, db)

        return {'result': 'ok'}

def rgb_to_xy(rgb):
    red, green, blue = rgb

    if( red > 0.04045):
        red = pow((red + 0.055) / (1.0 + 0.055), 2.4)
    else:
        red = (red / 12.92)

    if(green > 0.04045):
        green = pow((green + 0.055) / (1.0 + 0.055), 2.4)
    else: green = (green / 12.92)

    if(blue > 0.04045):
        blue = pow((blue + 0.055) / (1.0 + 0.055), 2.4)
    else:
        blue = (blue / 12.92)

    X = red * 0.664511 + green * 0.154324 + blue * 0.162028
    Y = red * 0.283881 + green * 0.668433 + blue * 0.047685
    Z = red * 0.000088 + green * 0.072310 + blue * 0.986039

    if (X+Y+Z) == 0:
        fx = 0
        fy = 0
        fz = 0
    else:
        fx = X / (X + Y + Z)
        fy = Y / (X + Y + Z)
        fz = Z / (X + Y + Z)

    if (fx != fx):
        fx = 0.0

    if (fy != fy):
        fy = 0.0

    if (fz != fz):
        fz = 0.0

    return (fx, fy, fz)

def get_devices(db):
    data = get_gateway(PHILIPS_HUE, db)
    ip = data['IP']
    user = data['KEY1']

    response = requests.get("http://" + ip + "/api/"+user+"/lights").text

    print response

    data = json.loads(response)

    ids = list(data.keys())

    devices = []

    for id in ids:
        item = data[id]
        device_item = {'title': item['name'], 'id': id, 'room': None, 'type': 'light'}
        devices.append(device_item)

    return {'devices': devices}

def get_light_info(id, db):
    data = get_gateway(PHILIPS_HUE, db)
    ip = data['IP']
    user = data['KEY1']

    request = requests.get("http://" + ip + "/api/" + user + "/lights/"+str(id))

    code = request.status_code

    if(code != 200):
        return False

    data = json.loads(request.text)

    mode = data['state']['on']
    brightness = int(float(data['state']['bri'])/255*100)
    saturation = int(float(data['state']['sat'])/255*100)
    hue = data['state']['hue']

    update_light_info(id, mode, hue, saturation, brightness, db)

    return True

def update_light_info(id, mode, hue, saturation, brightness, db):
    with db:
        cur = db.cursor()

        if saturation is None:
            saturation = 255

        if brightness is None:
            brightness = 255

        cur.execute("UPDATE PHILIPS_HUE_LIGHTS SET IS_ON = :mode, BRIGHTNESS = :bri, SATURATION = :sat, HUE = :hue WHERE ID = :id",
                    {'mode': mode, 'bri': brightness, 'sat': saturation, 'hue': hue, 'id': id})