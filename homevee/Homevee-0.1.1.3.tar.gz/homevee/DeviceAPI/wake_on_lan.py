import json
import os

from homevee.DeviceAPI import xbox_wol
from homevee.Helper.helper_functions import has_permission

def wake_on_lan(username, id, db, check_user=True):

    cur = db.cursor()
    cur.execute("SELECT * FROM WAKE_ON_LAN WHERE DEVICE == :id", {'id': id})

    device = cur.fetchone()

    if check_user and not has_permission(username, device['LOCATION'], db):
        return {'result': 'nopermission'}

    os.system("sudo wakeonlan "+device['MAC_ADDRESS'])

    cur.close()

    return {'status': 'ok'}

def get_wol_devices(username, room, db):
    if not has_permission(username, room, db):
        return {'status': 'nopermission'}

    devices = []

    cur = db.cursor()
    cur.execute("SELECT * FROM WAKE_ON_LAN WHERE LOCATION == :room", {'room': room})

    for data in cur.fetchall():
        devices.append({'name': data['NAME'], 'id': data['DEVICE'], 'icon': data['ICON']})

    return {'devices': devices}

def wake_xbox_on_lan(username, id, db, check_user=True):
    with db:
        cur = db.cursor()
        cur.execute("SELECT * FROM XBOX_ONE_WOL WHERE ID == :id",
                    {'id': id})

        device = cur.fetchone()

        if check_user and not has_permission(username, device['LOCATION'], db):
            return {'result': 'nopermission'}

        cur.close()

        ip = device['IP_ADDRESS']
        live_id = device['XBOX_LIVE_ID']

        xbox_wol.xbox_wake_up(ip, live_id)

        return {'status': 'ok'}

def get_xbox_devices(username, room, db):
    if not has_permission(username, room, db):
        return {'status': 'nopermission'}

    devices = []

    with db:
        cur = db.cursor()
        cur.execute("SELECT * FROM XBOX_ONE_WOL WHERE LOCATION == :room", {'room': room})

        for data in cur.fetchall():
            devices.append({'name': data['NAME'], 'id': data['ID'], 'icon': data['ICON']})

        cur.close()

        return {'devices': devices}