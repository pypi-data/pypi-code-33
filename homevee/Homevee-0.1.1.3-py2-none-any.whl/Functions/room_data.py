#!/usr/bin/python
# -*- coding: utf-8 -*-
from homevee.DeviceAPI.blind_control import get_blinds
from homevee.DeviceAPI.dimmer import get_dimmers
from homevee.DeviceAPI.energy_data import get_power_usage_devices
from homevee.DeviceAPI.get_modes import get_modes
from homevee.DeviceAPI.heating import get_thermostats
from homevee.DeviceAPI.rgb_control import get_rgb_devices
from homevee.DeviceAPI.toggle_devices import get_toggle_devices
from homevee.DeviceAPI.wake_on_lan import get_xbox_devices, get_wol_devices
from homevee.Functions.sensor_data import get_sensor_data
from homevee.Functions.triggers import get_triggers
from homevee.Helper.helper_functions import has_permission
from homevee.Manager.scenes import get_scenes
from homevee.device_types import *


def get_rooms(username, db):
    with db:
        cur = db.cursor()
        cur.execute("SELECT * FROM ROOMS")

        rooms = []

        for data in cur.fetchall():
            if has_permission(username, data['LOCATION'], db):
                rooms.append({'name': data['NAME'], 'location': data['LOCATION'], 'icon': data['ICON']})

        cur.close()

        return {'rooms': rooms}

def get_room_name(room_id, db):
    with db:
        cur = db.cursor()
        cur.execute("SELECT * FROM ROOMS WHERE LOCATION = :id", {'id': room_id})

        data = cur.fetchone()
        cur.close()
        return data['NAME']

def get_room_data(username, room, db):
    if not has_permission(username, room, db):
        return {'status': 'nopermission'}

    roomdata = []

    #Schalter abfragen
    switchdata = get_modes(username, room, "", "", db)
    for item in switchdata['modi']:
        if str(item['mode']) == "1":
            mode = True
        else:
            mode = False
        roomdata.append({'name': item['name'], 'id': item['device'], 'devicetype':item['type'],
            'icon': item['icon'], 'type': 'switch', 'value': ('true' if mode else 'false')})

    #Dimmer
    dimmerdata = get_dimmers(username, room, db)
    for item in dimmerdata['dimmer']:
        roomdata.append({'name': item['name'], 'id': item['device'], 'devicetype': item['type'],
                         'icon': item['icon'], 'type': 'dimmer', 'value': item['value']})
    #Toggle
    toggledata = get_toggle_devices(username, room, db)
    for item in toggledata['toggles']:
        roomdata.append({'name': item['name'], 'id': item['id'], 'devicetype':item['type'],
            'icon': item['icon'], 'type': 'toggle', 'value': ''})

    #Trigger
    triggerdata = get_triggers(username, room, db)
    for item in triggerdata['triggers']:
        roomdata.append({'name': item['name'], 'id': item['id'], 'devicetype':item['type'],
            'icon': item['icon'], 'type': 'trigger', 'value': ''})

    #RGB
    rgbdata = get_rgb_devices(username, room, db)
    for item in rgbdata['rgb']:
        print item
        roomdata.append({'name': item['name'], 'devicetype':item['type'], 'id': item['id'],
            'icon': item['icon'], 'type': 'rgb', 'value': item['value']})

    #Thermostate
    thermostat_data = get_thermostats(username, room, "", "", db)
    for item in thermostat_data['thermostats'][0]['thermostat_array']:
        roomdata.append({'name': item['name'], 'id': item['id'], 'devicetype': item['type'],
                         'icon': item['icon'], 'type': 'heating', 'value': item['data']['value'],
                         'step': 0.5, 'min': item['data']['min'], 'max': item['data']['max']})

    #Sensoren abfragen
    sensordata = get_sensor_data(username, room, "", "", True, db)

    #print sensordata

    for item in sensordata['values'][0]['value_array']:
        roomdata.append({'name': item['shortform'], 'id': item['id'], 'devicetype': item['device_type'],
                         'icon': item['icon'], 'type': "value", 'value': item['wert']})

    #Szenen abfragen
    scenedata = get_scenes(username, room, db)
    if len(scenedata['scenes']) > 0:
        roomdata.append({'name': "Szenen", 'id': "scenes", 'devicetype': "scenes",
                         'icon': "scenes", 'type': "scenes", 'value': ""})

    #WOL abfragen
    wol_devices = get_wol_devices(username, room, db)

    for item in wol_devices['devices']:
        roomdata.append({'name': item['name'], 'id': item['id'], 'devicetype': WAKE_ON_LAN,
                         'icon': item['icon'], 'type': 'wakeonlan'})

    #XBOX ONE WOL abfragen
    xbox_devices = get_xbox_devices(username, room, db)

    for item in xbox_devices['devices']:
        roomdata.append({'name': item['name'], 'id': item['id'], 'devicetype': XBOX_ONE_WOL,
                         'icon': item['icon'], 'type': 'xboxone'})

    #Jalousie-Steuerung
    blind_controls = get_blinds(username, room, db)['blinds']
    for item in blind_controls:
        roomdata.append({'name': item['name'], 'id': item['id'], 'devicetype': item['type'],
                         'icon': item['icon'], 'type': 'blinds', 'value': item['value']})

    #Strom-Messgeräte
    power_usage_devices = get_power_usage_devices(username, room, db)
    for item in power_usage_devices:
        roomdata.append({'name': item['name'], 'id': item['id'], 'devicetype': item['devicetype'],
                         'icon': item['icon'], 'type': 'value', 'value': item['value']})

    return {'roomdata': roomdata}

'''<?php
	
    //Neu dazugekommen
	$reeddata = getReedData($room, "", "", $db);
    foreach($reeddata['values'][0]['value_array'] as $reed){
		//Die Werte des Arrays wurden angepasst
        array_push($roomdata, array('name' => $reed['shortform'], 'device' => $reed['id'],
		'icon' => $reed['icon'], 'type' => "reed", 'device_type' => $reed['device_type'], 'value' => $reed['wert']));
    }
	
	$presencedata = getPresenceData($room, "", "", $db);
    foreach($presencedata['values'][0]['value_array'] as $presence){
        array_push($roomdata, array('name' => $presence['shortform'], 'device' => $presence['id'],
		'icon' => $presence['icon'], 'type' => "presence", 'device_type' => $presence['device_type'], 'value' => $presence['wert']));
    }
	
    $diydata = getDIYDevices($room, $db);
    foreach($diydata['diydevices'] as $device){
        array_push($roomdata, array('name' => $device['name'], 'device' => $device['device'], 'icon' => $device['icon'],
		'type' => 'diydevice', 'value' => "", 'device_type' => "DIY Gerät"));
    }
	
    $dimmer = getDimmers($room, $db);
    foreach($dimmer['dimmers'] as $device){
        array_push($roomdata, array('name' => $device['name'], 'device' => $device['id'], 'icon' => $device['icon'],
		'type' => 'dimmer', 'value' => $device['value'], 'device_type' => $device['device_type']));
    }
	
    $powermeters = getPowerMeterData($room, "", "", "", $db);
	
    foreach($powermeters['powermeters'][0]['value_array'] as $device){
        array_push($roomdata, array('name' => $device['name'], 'device' => $device['id'], 'icon' => $device['icon'],
		'type' => 'powermeter', 'value' => $device['value'], 'device_type' => $device['device_type']));
    }
	
	//IP-Kameras abfragen
	$ipcameras = getIpCameraData($room, "", $db);
	
    foreach($ipcameras['ipcameras'][0]['value_array'] as $device){
        array_push($roomdata, array('name' => $device['name'], 'device' => $device['id'], 'icon' => $device['icon'],
		'type' => 'ipcamera', 'value' => $device['value'], 'device_type' => $device['device_type'],
		'url' => $device['url'], 'username' => $device['username'], 'password' => $device['password']));
    }
	
    //Thermostate
	$thermostats = getHeatingData($room, "", "", "1", $db);
	
    foreach($thermostats['thermostats'][0]['thermostat_array'] as $thermostat){
        array_push($roomdata, array('name' => $thermostat['name'], 'device' => $thermostat['id'],
		'icon' => $thermostat['icon'], 'type' => "heating", 'device_type' => $thermostat['device_type'], 'value' => $thermostat['data']['value'],
		'einheit' => $thermostat['data']['einheit'], 'min' => $thermostat['data']['min'], 'max' => $thermostat['data']['max'], 'step' => 0.5));
    }
	
	//WOL-Geräte
	$devices = getWakeOnLanDevices($room, $db);
	
    foreach($devices['devices'] as $device){
        array_push($roomdata, array('name' => $device['name'], 'device' => $device['id'],
		'icon' => $device['icon'], 'type' => "wakeonlan", 'device_type' => "Wake on Lan Gerät", 'value' => "Wake on Lan"));
    }
	
	//XBOX One
	$devices = getXboxOneDevices($room, $db);
	
    foreach($devices['devices'] as $device){
        array_push($roomdata, array('name' => $device['name'], 'device' => $device['id'],
		'icon' => $device['icon'], 'type' => "xboxone", 'device_type' => "XBOX One", 'value' => "Hochfahren"));
    }
     
    return array('roomdata' => $roomdata);
}
 
?>'''