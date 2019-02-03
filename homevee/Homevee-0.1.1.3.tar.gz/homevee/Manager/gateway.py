#!/usr/bin/python
# -*- coding: utf-8 -*-
import json
import time

import requests

import homevee.gateway_keys
from homevee.Helper.helper_functions import has_permission


def get_gateway(key, db):
    cur = db.cursor()
    cur.execute("SELECT * FROM GATEWAYS WHERE NAME == :key", {'key': key})

    data = cur.fetchone()

    cur.close()

    return data

def add_edit_gateway(username, type, user, password, change_pw, ip, port, gateway_type, db):
    if not has_permission(username, "admin", db):
        return {'status': 'noadmin'}

    param_array = {'name': type, 'ip': ip, 'port': port, 'key1': user, 'type': gateway_type}

    with db:
        cur = db.cursor()

        if change_pw == "true":
            param_array['key2'] = password

            cur.execute("UPDATE OR IGNORE 'GATEWAYS' SET IP = :ip, PORT = :port, KEY1 = :key1, KEY2 = :key2 TYPE = :type, WHERE NAME = :name;",
                        param_array)

            cur.execute("INSERT OR IGNORE INTO 'GATEWAYS' (NAME, IP, PORT, KEY1, KEY2, TYPE) VALUES (:name, :ip, :port, :key1, :key2, :type);",
                        param_array)
        else:
            cur.execute("UPDATE OR IGNORE 'GATEWAYS' SET IP = :ip, PORT = :port, KEY1 = :key1 WHERE NAME = :name;",
                        param_array)

            cur.execute("INSERT OR IGNORE INTO 'GATEWAYS' (NAME, IP, PORT, KEY1, TYPE) VALUES (:name, :ip, :port, :key1, :type);",
                        param_array)

    return {'result': 'ok'}

def delete_gateway(username, key, db):
    if not has_permission(username, "admin", db):
        return {'status': 'noadmin'}

    with db:
        cur = db.cursor()
        cur.execute("DELETE FROM GATEWAYS WHERE NAME == :key", {'key': key})

        cur.close()

        #Abfrage erfolgreich?
        if True:
            return {'status': 'ok'}
        else:
            return {'status': 'error'}

def get_gateways(username, db):
    if not has_permission(username, "admin", db):
        return {'status': 'noadmin'}

    with db:
        cur = db.cursor()
        cur.execute("SELECT * FROM GATEWAYS")

        gateways = []

        for gateway in cur.fetchall():
            gateways.append({'name': gateway['NAME'], 'ip': gateway['IP'], 'port': gateway['PORT'],
                             'key1': gateway['KEY1'], 'type': gateway['TYPE']})

        cur.close()

        return {'gateways': gateways, 'gatewaytypesleft': get_gateway_types(username, db)}

def get_gateway_types(username, db):
    if not has_permission(username, "admin", db):
        return {'status': 'noadmin'}

    gateway_types = [
        {'key': gateway_keys.Z_WAVE, 'type': 'user'},
        {'key': gateway_keys.FUNKSTECKDOSEN, 'type': 'url'},
        {'key': gateway_keys.MAX_CUBE, 'type': 'url'},
        {'key': gateway_keys.MQTT_BROKER, 'type': 'user'},
        {'key': gateway_keys.PHILIPS_HUE, 'type': 'apikey'},
        {'key': gateway_keys.MIYO_CUBE, 'type': 'apikey'},
        {'key': gateway_keys.RADEMACHER_HOMEPILOT, 'type': 'url'},
    ]

    with db:
        cur = db.cursor()
        cur.execute("SELECT NAME FROM GATEWAYS")

        for gateway in cur.fetchall():
            name = gateway['NAME']
            for i in range(0, len(gateway_types)-1):
                if gateway_types[i]['key'] == name:
                    del gateway_types[i]

        cur.close()

        return gateway_types

def connect_gateway(username, type, ip, db):
    if not has_permission(username, "admin", db):
        return {'result': 'noadmin'}

    if type == gateway_keys.PHILIPS_HUE:
        while True:
            print "try connecting..."

            data = {"devicetype": "homevee#system"}

            response = requests.post("http://" + ip + "/api", data=json.dumps(data))

            result = response.text

            print "result: "+result

            result = json.loads(result)

            result = result[0]

            if "error" in result:
                if result['error']['type'] == 101:
                    return {'result': 'error', 'msg': 'Drücke bitte die Taste auf deinem Philips Hue Gateway.'}
            elif "success" in result:
                user = result['success']['username']

                add_edit_gateway(username, type, user, "", "", ip, "80", "apikey", db)

                return {'result': 'ok'}
    elif type == gateway_keys.MIYO_CUBE:
        while True:
            print "try connecting..."

            response = requests.get("http://" + ip + "/api/link")

            result = response.text

            print "result: "+result

            result = json.loads(result)

            if "error" in result:
                if result['errorLoc'] == "NOTIFY_ERROR_LINKINACTIVE":
                    return {'result': 'error', 'msg': 'Drücke bitte die Taste hinten auf deinem MIYO Cube.'}
            elif "success" in result:
                user = result['success']['username']

                add_edit_gateway(username, type, user, "", "", ip, "80", "apikey", db)

                return {'result': 'ok'}
    else:
        return {'result': 'error'}