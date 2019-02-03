#!/usr/bin/python
# -*- coding: utf-8 -*-

from pymax.cube import Cube

from homevee.Manager.gateway import get_gateway


def get_devices(ip):
    thermostats = []
    try:
        with Cube(ip) as cube:
            for room in cube.rooms:
                for device in room.devices:
                    print device
                    thermostat = {'title': device.name, 'id': device.serial, 'room': room.name}

                    thermostats.append(thermostat)
    except:
        thermostats = []

    return thermostats


def set_temp(id, value, db):
    gateway_data = get_gateway("MAX! Cube", db)

    try:
        with Cube(gateway_data['IP']) as cube:
            for room in cube.rooms:
                for device in room.devices:
                    if id == device.serial:
                        result = cube.set_mode_manual(room.room_id, room.rf_address, float(value))

                        print(result)

                        with db:
                            cur = db.cursor()

                            cur.execute("UPDATE MAX_THERMOSTATS SET LAST_TEMP = :temp WHERE ID == :id",
                                        {'temp': value, 'id': id})

                        return {'result': 'ok'}
    except:
        return {'result': 'error'}