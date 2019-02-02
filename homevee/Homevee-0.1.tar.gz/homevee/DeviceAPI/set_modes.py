#!/usr/bin/python
# -*- coding: utf-8 -*-
import os
import traceback
import urllib2
from homevee.device_types import *
from homevee.DeviceAPI import zwave
from homevee.Helper.helper_functions import has_permission
from homevee.Manager.gateway import get_gateway


def set_modes(username, type, id, mode, db, check_user=True):
    if type == FUNKSTECKDOSE:
        return set_socket(username, id, mode, db, check_user)
    elif type == ZWAVE_SWITCH:
        return set_zwave_switch(username, id, mode, db, check_user)
    elif type == URL_SWITCH:
        return set_url_switch_binary(username, id, mode, db, check_user)
    elif type == URL_TOGGLE:
        return set_url_toggle(username, id, db, check_user)
    else:
        raise ValueError("Type does not exist")

def set_url_switch_binary(username, id, mode, db, check_user=True):
    with db:
        cur = db.cursor()
        cur.execute("SELECT * FROM URL_SWITCH_BINARY WHERE ID == :id",
                    {'id': id})

        data = cur.fetchone()

        if check_user and not has_permission(username, data['LOCATION'], db):
            return {'result': 'nopermission'}

        if mode == "":
            urllib2.urlopen(data['URL_ON'])
        else:
            urllib2.urlopen(data['URL_OFF'])

    return {'status': 'ok'}

def set_url_toggle(username, id, db, check_user=True):
    with db:
        cur = db.cursor()
        cur.execute("SELECT * FROM URL_TOGGLE WHERE ID == :id",
                    {'id': id})

        data = cur.fetchone()

        if check_user and not has_permission(username, data['LOCATION'], db):
            return {'result': 'nopermission'}

        urllib2.urlopen(data['TOGGLE_URL'])

    return {'status': 'ok'}

def set_socket(username, id, mode, db, check_user=True):
    with db:
        cur = db.cursor()
        cur.execute("SELECT * FROM FUNKSTECKDOSEN WHERE DEVICE == :device",
                    {'device': id})

        data = cur.fetchone()

        if check_user and not has_permission(username, data['ROOM'], db):
            return {'result': 'nopermission'}

        housecode = data['HAUSCODE']
        socketnum = data['STECKDOSENNUMMER']

        gateway = get_gateway('Funksteckdosen-Controller', db)
        print gateway

        if gateway is None or gateway['IP'] == 'localhost' or gateway['IP'] == '127.0.0.1':
            os.system("/usr/local/bin/send "+str(housecode)+" "+str(socketnum)+" "+str(mode))
        else:
            url = 'http://'+str(gateway['IP'])+'/funksteckdose.php?hauscode='+str(housecode)+\
                  '&steckdosennummer='+str(socketnum)+"&zustand="+str(mode)
            print url
            urllib2.urlopen(url)

        cur.execute("UPDATE FUNKSTECKDOSEN SET ZUSTAND = :zustand WHERE DEVICE == :device",
            {'zustand': mode, 'device': id})

        cur.close()

        return {'status': 'ok'}

def set_zwave_switch(username, id, mode, db, check_user=True):
    try:
        with db:
            cur = db.cursor()
            cur.execute("SELECT * FROM ZWAVE_SWITCHES WHERE ID == :device",
                        {'device': id})

            data = cur.fetchone()

            if check_user and not has_permission(username, data['LOCATION'], db):
                return {'result': 'nopermission'}

            device_id = data['ID']

            state = "on" if (int(mode) == 1) else "off"

            result = zwave.device_control.set_binary_device(device_id, state, db)

            if result['code'] == 200:
                cur.execute("UPDATE ZWAVE_SWITCHES SET VALUE = :value WHERE ID = :id",
                            {'value': mode, 'id': id})

                return {'result': 'ok'}
    except Exception, e:
        traceback.print_exc()
        return {'result': 'error'}

def set_diy_switch(id, mode, db, check_user=True):
    return