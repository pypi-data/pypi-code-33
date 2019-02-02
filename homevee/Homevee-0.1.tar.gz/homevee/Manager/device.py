#!/usr/bin/python
# -*- coding: utf-8 -*-
import json

import os

from homevee.Functions.room_data import get_rooms
from homevee.Functions.sensor_data import SENSOR_TYPE_MAP
from homevee.device_types import *
from homevee.DeviceAPI import max_cube, zwave, philips_hue, rademacher_homepilot
from homevee.Helper.helper_functions import has_permission
from homevee.Manager.gateway import get_gateway
from homevee.gateway_keys import *


def get_gateway_devices(username, type, db):
    if not has_permission(username, "admin", db):
        return {'status': 'noadmin'}

    if type == Z_WAVE:
        return zwave.get_devices.get_devices(db)
    if type == PHILIPS_HUE_LIGHT:
        return philips_hue.get_devices(db)
    if type == RADEMACHER_HOMEPILOT:
        return rademacher_homepilot.get_devices(db)
    elif type == MAX_CUBE:
        ip = get_gateway("MAX! Cube", db)['IP']

        print ip

        devices = max_cube.get_devices(ip)

        if devices is not None:
            return {'devices': devices}
        else:
            return {'devices': []}
    elif type == "Network":
        network_devices = []

        hostnames = os.popen("arp -a").read()

        ip_adresses = os.popen("arp -a").read()

        print hostnames
        #print ip_adresses

        #for i in range(0, len(hostnames)):

        return {'devices': network_devices}
    else:
        return "nosuchgateway"

'''
function getGatewayDevices($type, $db){
	switch($type){
		case "Network":
			$networkDevices = array();

			exec("arp", $hostnames);
			exec("arp -n", $ipAdresses);

			for($i = 1; $i < sizeOf($hostnames); $i++){

				$names = preg_replace('!\s+!', ' ', $hostnames[$i]);

				$name = explode(" ", $names)[0];

				$adresses = preg_replace('!\s+!', ' ', $ipAdresses[$i]);

				$data = explode(" ", $adresses);

				$ip = $data[0];

				$mac = $data[2];

				array_push($networkDevices, array('id' => $ip, 'title' => $name, 'id2' => $mac));
			}

			return array('devices' => $networkDevices);
		default:
			return "nosuchgateway";
	}
}
'''

def add_edit_device(username, device_id, type, data, db):
    if not has_permission(username, "admin", db):
        return {'status': 'noadmin'}

    add_new = (device_id == None or device_id == "" or device_id == "-1")

    type = type.decode("utf-8")

    data_array = json.loads(data)

    with db:
        cur = db.cursor()

        #XBOX One WOL
        if type == XBOX_ONE_WOL:
            param_array = {'room': data_array['room'], 'name': data_array['name'], 'icon': data_array['icon'],
                           'ip': data_array['ip'], 'live_id': data_array['liveid']}

            if device_id == "-1" or device_id is -1:
                cur.execute(
                    "INSERT OR IGNORE INTO 'XBOX_ONE_WOL' (LOCATION, ICON, NAME, IP_ADDRESS, XBOX_LIVE_ID) VALUES (:room, :icon, :name, :ip, :live_id);",
                    param_array)
            else:

                param_array['id'] = device_id

                cur.execute(
                    "UPDATE OR IGNORE 'XBOX_ONE_WOL' SET LOCATION = :room, ICON = :icon, NAME = :name, IP_ADDRESS = :ip, XBOX_LIVE_ID = :live_id WHERE ID == :id;",
                    param_array)

        # Philips Hue
        elif type == PHILIPS_HUE_LIGHT:
            param_array = {'room': data_array['room'], 'name': data_array['name'], 'icon': data_array['icon'], 'id': device_id}

            cur.execute(
                "INSERT OR IGNORE INTO 'PHILIPS_HUE_LIGHTS' (LOCATION, ID, ICON, NAME) VALUES (:room, :id, :icon, :name);",
                param_array)

            cur.execute(
                "UPDATE OR IGNORE 'PHILIPS_HUE_LIGHTS' SET LOCATION = :room, ICON = :icon, NAME = :name WHERE ID == :id;",
                param_array)
        #MQTT Sensor
        elif type == MQTT_SENSOR:
            param_array = {'room': data_array['room'], 'name': data_array['name'], 'icon': data['icon'], 'id': device_id,
                           'key': data_array['key'], 'topic': data_array['topic'], 'save_data': data_array['save_data']}

            cur.execute(
                "INSERT OR IGNORE INTO 'MQTT_SENSORS' (ROOM, ID, ICON, NAME, KEY, TOPIC, SAVE_DATA) VALUES (:room, :id, :icon, :name, :key, :topic, :save_data);",
                param_array)

            cur.execute(
                "UPDATE OR IGNORE 'MQTT_SENSORS' SET ROOM = :room, ICON = :icon, NAME = :name, KEY = :key, TOPIC = :topic, SAVE_DATA = :save_data, WHERE ID == :id;",
                param_array)

        #433 MHz
        elif type == FUNKSTECKDOSE:
            param_array = {'room': data_array['room'], 'name': data_array['name'], 'icon': data_array['icon'],
                           'hauscode': data_array['hauscode'], 'nummer': data_array['steckdosennummer']}

            '''if add_new:
                            cur.execute("SELECT COUNT(*) FROM 'funksteckdosen' WHERE HAUSCODE = :hauscode AND STECKDOSENNUMMER = :nummer;",
                                        {'hauscode': data_array['hauscode'], 'nummer': data_array['steckdosennummer']})

                            count = cur.fetchone()['COUNT(*)']

                            if(int(count) != 0):
                                return "hauscodesocketnumberinuse"
                        else:
                            param_array['id'] = device_id'''

            if add_new:
                cur.execute("INSERT INTO 'funksteckdosen' (ROOM, HAUSCODE, STECKDOSENNUMMER, ICON, NAME) VALUES (:room, :hauscode, :nummer, :icon, :name);",
                            param_array)
            else:
                param_array['id'] = device_id

                cur.execute("UPDATE 'funksteckdosen' SET ROOM = :room, HAUSCODE = :hauscode, STECKDOSENNUMMER = :nummer, ICON = :icon, NAME = :name WHERE DEVICE == :id;",
                            param_array)
        # MAX!
        elif type == MAX_THERMOSTAT:
            param_array = {'room': data_array['room'], 'name': data_array['name'],
                           'icon': data_array['icon'], 'id': device_id}

            cur.execute("UPDATE OR IGNORE 'MAX_THERMOSTATS' SET RAUM = :room, NAME = :name, ICON = :icon WHERE ID = :id;",
                param_array)

            cur.execute("INSERT OR IGNORE INTO 'MAX_THERMOSTATS' (RAUM, ID, NAME, ICON) VALUES (:room, :id, :name, :icon);",
                param_array)
        # Rademacher!
        elif type == RADEMACHER_THERMOSTAT:
            param_array = {'room': data_array['room'], 'name': data_array['name'],
                           'icon': data_array['icon'], 'id': device_id}

            cur.execute("UPDATE OR IGNORE 'HOMEPILOT_THERMOSTATS' SET ROOM = :room, NAME = :name, ICON = :icon WHERE ID = :id;",
                param_array)

            cur.execute("INSERT OR IGNORE INTO 'HOMEPILOT_THERMOSTATS' (ROOM, ID, NAME, ICON) VALUES (:room, :id, :name, :icon);",
                param_array)
        elif type == RADEMACHER_BLIND_CONTROL:
            param_array = {'room': data_array['room'], 'name': data_array['name'],
                           'icon': data_array['icon'], 'id': device_id}

            cur.execute("UPDATE OR IGNORE 'HOMEPILOT_BLIND_CONTROL' SET LOCATION = :room, NAME = :name, ICON = :icon WHERE ID = :id;",
                param_array)

            cur.execute("INSERT OR IGNORE INTO 'HOMEPILOT_BLIND_CONTROL' (LOCATION, ID, NAME, ICON) VALUES (:room, :id, :name, :icon);",
                param_array)

        #Z-Wave
        elif type == ZWAVE_SENSOR:
            param_array = {'room': data_array['room'], 'savedata': data_array['savedata'], 'shortform': data_array['name'],
                           'sensor_type': data_array['sensor_type'], 'icon': data_array['icon'], 'id': device_id}

            cur.execute("SELECT COUNT(*) FROM ZWAVE_SENSOREN WHERE ID = :id", {'id': device_id})
            add_new = (cur.fetchone()['COUNT(*)'] == 0)

            if add_new:
                cur.execute("INSERT INTO 'ZWAVE_SENSOREN' (RAUM, ID, SHORTFORM, ICON, SAVE_DATA, SENSOR_TYPE) VALUES (:room, :id, :shortform, :icon, :savedata, :sensor_type);",
                            param_array)
            else:
                cur.execute("UPDATE 'ZWAVE_SENSOREN' SET RAUM = :room, SHORTFORM = :shortform, ICON = :icon, SAVE_DATA = :savedata, SENSOR_TYPE = :sensor_type WHERE ID = :id;",
                            param_array)
        elif type == ZWAVE_THERMOSTAT:
            param_array = {'room': data_array['room'], 'name': data_array['name'], 'icon': data_array['icon'], 'id': device_id}

            cur.execute("SELECT COUNT(*) FROM ZWAVE_THERMOSTATS WHERE THERMOSTAT_ID = :id", {'id': device_id})
            add_new = (cur.fetchone()['COUNT(*)'] == 0)

            if add_new:
                cur.execute("INSERT INTO 'ZWAVE_THERMOSTATS' (RAUM, NAME, THERMOSTAT_ID, ICON) VALUES (:room,:name,:id,:icon);",
                param_array)
            else:
                cur.execute("UPDATE 'ZWAVE_THERMOSTATS' SET RAUM = :room, NAME = :name, THERMOSTAT_ID = :id, ICON =:icon WHERE THERMOSTAT_ID = :id;",
                param_array)
        elif type == ZWAVE_POWER_METER:
            param_array = {'room': data_array['room'], 'name': data_array['name'], 'icon': data_array['icon'], 'id': device_id, 'daily_reset': data_array['is_reset_daily']}

            cur.execute("SELECT COUNT(*) FROM ZWAVE_POWER_METER WHERE DEVICE_ID = :id", {'id': device_id})
            add_new = (cur.fetchone()['COUNT(*)'] == 0)

            if add_new:
                cur.execute("INSERT INTO 'ZWAVE_POWER_METER' (ROOM_ID, DEVICE_ID, DEVICE_NAME, ICON, IS_RESET_DAILY) VALUES (:room,:id,:name,:icon,:daily_reset);",
                param_array)
            else:
                cur.execute("UPDATE 'ZWAVE_POWER_METER' SET ROOM_ID = :room, DEVICE_NAME = :name, DEVICE_ID = :id, ICON =:icon, IS_RESET_DAILY = :daily_reset WHERE DEVICE_ID =:id;",
                param_array)
        elif type == ZWAVE_SWITCH:
            param_array = {'room': data_array['room'], 'name': data_array['name'], 'icon': data_array['icon'], 'id': device_id}

            cur.execute("SELECT COUNT(*) FROM ZWAVE_SWITCHES WHERE ID = :id", {'id': device_id})
            add_new = (cur.fetchone()['COUNT(*)'] == 0)

            if add_new:
                cur.execute("INSERT INTO 'ZWAVE_SWITCHES' (LOCATION, NAME, ID, ICON) VALUES (:room,:name,:id,:icon);",
                param_array)
            else:
                cur.execute("UPDATE 'ZWAVE_SWITCHES' SET LOCATION = :room, NAME = :name, ID = :id, ICON =:icon WHERE ID =:id;",
                param_array)
        elif type == ZWAVE_DIMMER:
            param_array = {'room': data_array['room'], 'name': data_array['name'], 'icon': data_array['icon'], 'id': device_id}

            cur.execute("SELECT COUNT(*) FROM ZWAVE_DIMMER WHERE ID = :id", {'id': device_id})
            add_new = (cur.fetchone()['COUNT(*)'] == 0)

            if add_new:
                cur.execute("INSERT INTO 'ZWAVE_DIMMER' (LOCATION, NAME, ID, ICON) VALUES (:room,:name,:id,:icon);",
                param_array)
            else:
                cur.execute("UPDATE 'ZWAVE_DIMMER' SET LOCATION = :room, NAME = :name, ID = :id, ICON =:icon WHERE ID =:id;",
                param_array)
        #Media Center
        elif type == MEDIA_CENTER:
            param_array = {'room': data_array['room'], 'name': data_array['name'], 'ip': data_array['ip'],
                           'username': data_array['username'], 'password': data_array['password'], 'type': data_array['type']}

            if add_new:
                cur.execute("INSERT INTO 'MEDIA_CENTER' (LOCATION, NAME, IP, USERNAME, PASSWORD, TYPE) VALUES (:room,:name, :ip, :username, :password, :type);",
                param_array)
            else:
                param_array['id'] = device_id
                cur.execute("UPDATE 'MEDIA_CENTER' SET LOCATION = :room, NAME = :name, IP = :id, USERNAME = :username, PASSWORD = :password, TYPE = :type, ICON =:icon WHERE ID = :id;",
                param_array)
        #URL-Devices
        elif type == URL_SWITCH:
            param_array = {'room': data_array['room'], 'name': data_array['name'], 'on': data_array['onurl'],
                           'off': data_array['offurl'], 'val': data_array['valurl'], 'icon': data_array['icon']}

            if add_new:
                cur.execute("INSERT INTO 'URL_SWITCH_BINARY' (LOCATION, NAME, URL_ON, URL_OFF, URL_GET_STATE, ICON) VALUES (:room,:name, :on, :off, :val, :icon);",
                param_array)
            else:
                param_array['id'] = device_id
                cur.execute("UPDATE 'URL_SWITCH_BINARY' SET LOCATION = :room, NAME = :name, URL_ON = :on, URL_OFF = :off, URL_GET_STATE = :val, ICON =:icon WHERE ID = :id;",
                param_array)
        elif type == URL_TOGGLE:
            param_array = {'room': data_array['room'], 'name': data_array['name'], 'toggle': data_array['toggleurl'],
                           'icon': data_array['icon']}

            if add_new:
                cur.execute("INSERT INTO 'URL_TOGGLE' (LOCATION, NAME, TOGGLE_URL, ICON) VALUES (:room, :name, :toggle, :icon);",
                param_array)
            else:
                param_array['id'] = device_id
                cur.execute("UPDATE 'URL_TOGGLE' SET LOCATION = :room, NAME = :name, TOGGLE_URL = :toggle, ICON =:icon WHERE ID = :id;",
                param_array)
        elif type == URL_RGB_LIGHT:
            param_array = {'room': data_array['room'], 'name': data_array['name'], 'url': data_array['url'],
                           'icon': data_array['icon']}

            if add_new:
                cur.execute("INSERT INTO 'URL_RGB_LIGHT' (LOCATION, NAME, URL, ICON) VALUES (:room, :name, :url, :icon);",
                param_array)
            else:
                param_array['id'] = device_id
                cur.execute("UPDATE 'URL_RGB_LIGHT' SET LOCATION = :room, NAME = :name, URL = :toggle, ICON =:icon WHERE ID = :id;",
                param_array)
        #MQTT
        elif type == MQTT_TRIGGER:
            param_array = {'room': data_array['room'], 'name': data_array['name'], 'topic': data_array['topic'],
                           'icon': data_array['icon'], 'type': data_array['type']}

            if add_new:
                cur.execute("INSERT INTO 'MQTT_TRIGGERS' (LOCATION, NAME, TOPIC, TYPE, ICON) VALUES (:room, :name, :topic, :type, :icon);",
                param_array)
            else:
                param_array['id'] = device_id
                cur.execute("UPDATE 'MQTT_TRIGGERS' SET LOCATION = :room, NAME = :name, TOPIC = :topic, ICON =:icon WHERE ID = :id;",
                param_array)
        elif type == MQTT_SENSOR:
            param_array = {'room': data_array['room'], 'name': data_array['name'], 'topic': data_array['topic'],
                           'icon': data_array['icon'], 'type': data_array['type']}

            if add_new:
                cur.execute("INSERT INTO 'MQTT_SENSORS' (LOCATION, NAME, TOPIC, TYPE, ICON) VALUES (:room, :name, :topic, :type, :icon);",
                param_array)
            else:
                param_array['id'] = device_id
                cur.execute("UPDATE 'MQTT_SENSORS' SET LOCATION = :room, NAME = :name, TOPIC = :topic, ICON =:icon WHERE ID = :id;",
                param_array)
        #Wake on Lan
        elif type == WAKE_ON_LAN:
            param_array = {'room': data_array['room'], 'name': data_array['name'],
                           'icon': data_array['icon'], 'mac': data_array['mac']}

            if add_new:
                cur.execute("INSERT INTO 'WAKE_ON_LAN' (LOCATION, NAME, ICON, MAC_ADDRESS) VALUES (:room, :name, :icon, :mac);",
                param_array)
            else:
                param_array['id'] = device_id
                cur.execute("UPDATE 'WAKE_ON_LAN' SET LOCATION = :room, NAME = :name, MAC_ADDRESS = :mac, ICON =:icon WHERE DEVICE = :id;",
                param_array)
        else:
            return {'result': 'nosuchtype'}

    return {'result': 'ok'}

def delete_device(username, type, id, db):
    type = type.encode('utf-8')

    with db:
        cur = db.cursor()

        db_cols = {
            FUNKSTECKDOSE: {'table': 'FUNKSTECKDOSEN', 'location': 'ROOM', 'id': 'DEVICE'},
            PHILIPS_HUE_LIGHT: {'table': 'PHILIPS_HUE_LIGHTS', 'location': 'LOCATION', 'id': 'ID'},
            WAKE_ON_LAN: {'table': 'WAKE_ON_LAN', 'location': 'LOCATION', 'id': 'DEVICE'},
            XBOX_ONE_WOL: {'table': 'XBOX_ONE_WOL', 'location': 'LOCATION', 'id': 'ID'},
            URL_RGB_LIGHT: {'table': 'URL_RGB_LIGHT', 'location': 'LOCATION', 'id': 'ID'},
            MQTT_SENSOR: {'table': 'MQTT_SENSORS', 'location': 'ROOM', 'id': 'ID'},
            URL_TOGGLE: {'table': 'URL_TOGGLE', 'location': 'LOCATION', 'id': 'ID'},
            URL_SWITCH: {'table': 'URL_SWITCH', 'location': 'LOCATION', 'id': 'ID'},
            ZWAVE_DIMMER: {'table': 'ZWAVE_DIMMER', 'location': 'LOCATION', 'id': 'ID'},
            ZWAVE_SWITCH: {'table': 'ZWAVE_SWITCHES', 'location': 'LOCATION', 'id': 'ID'},
            ZWAVE_SENSOR: {'table': 'ZWAVE_SENSOREN', 'location': 'RAUM', 'id': 'ID'},
            ZWAVE_POWER_METER: {'table': 'ZWAVE_POWER_METER', 'location': 'ROOM_ID', 'id': 'DEVICE_ID'},
            ZWAVE_THERMOSTAT: {'table': 'ZWAVE_THERMOSTATS', 'location': 'RAUM', 'id': 'THERMOSTAT_ID'},
            MAX_THERMOSTAT: {'table': 'MAX_THERMOSTATS', 'location': 'RAUM', 'id': 'ID'},
            RADEMACHER_THERMOSTAT: {'table': 'HOMEPILOT_THERMOSTATS', 'location': 'ROOM', 'id': 'ID'},
            RADEMACHER_BLIND_CONTROL: {'table': 'HOMEPILOT_BLIND_CONTROL', 'location': 'LOCATION', 'id': 'ID'}
        }

        if type not in db_cols:
            return {'result': 'nosuchtype'}

        cur.execute("SELECT * FROM "+db_cols[type]['table']+" WHERE "+db_cols[type]['id']+" = :id",
                    {'id': id})

        data = cur.fetchone()

        print(data)

        if not has_permission(username, data[db_cols[type]['location']], db):
            return {'result': 'nopermission'}

        cur.execute("DELETE FROM "+db_cols[type]['table']+" WHERE " + db_cols[type]['id'] + " = :id",
                    {'id': id})

        return {'result': 'ok'}

'''
function addEditDevice($deviceId, $type, $data, $db){
	if(!hasPermission("admin", $db)){
		return "noadmin";
	}
	
	$addNew = ($deviceId == null || $deviceId == "" || $deviceId == "-1");
	
	$type = utf8_decode($type);
	
	$dataArray = json_decode($data, true);
	
	switch($type){
		//Z-Wave
		case "Z-Wave Dimmer":
			$paramArray = array("room" => $dataArray['room'], "name" => $dataArray['name'], "icon" => $dataArray['icon']);
			
			if($addNew){
				$query = $db->prepare("INSERT INTO 'ZWAVE_DIMMER' (LOCATION, NAME, ID, ICON)
									VALUES (:room, :name, :id, :icon);");
			}	
			else{
				$query = $db->prepare("UPDATE 'ZWAVE_DIMMER' SET LOCATION = :room, NAME = :name, ID = :id,
									ICON = :icon WHERE ID = :id;");
			}
			
			//Z-Wave Dimmer bearbeiten bzw. hinzufügen
			break;
		//DIY
		case "DIY Fensterkontakt":
			$paramArray = array("room" => $dataArray['room'], "name" => $dataArray['name'], "ip" => $dataArray['ip'],
			"icon" => $dataArray['icon'], "channel" => $dataArray['channel']);
			
			if($addNew){
				$query = $db->prepare("INSERT INTO 'DIY_REEDSENSORS' (RAUM, ICON, IP, NAME, CHANNEL)
									VALUES (:room, :icon, :ip, :name, :channel);");
			}	
			else{
				$query = $db->prepare("UPDATE 'DIY_REEDSENSORS' SET RAUM = :room, ICON = :icon, IP = :ip, NAME = :name, 
					CHANNEL = :channel WHERE ID = :id;");
			}
			
			//DIY Sensor bearbeiten bzw. hinzufügen
			break;
		case "DIY Sensor":
			$paramArray = array("room" => $dataArray['room'], "name" => $dataArray['name'], "ip" => $dataArray['ip'], "savedata" => $dataArray['savedata'],
				"einheit" => $dataArray['einheit'], "icon" => $dataArray['icon'], "channel" => $dataArray['channel']);
			
			if($addNew){
				$query = $db->prepare("INSERT INTO 'DIY_SENSORS' (RAUM, ICON, IP, NAME, EINHEIT, SAVE_DATA, CHANNEL)
									VALUES (:room, :icon, :ip, :name, :einheit, :savedata, :channel);");
			}	
			else{
				$query = $db->prepare("UPDATE 'DIY_SENSORS' SET RAUM = :room, ICON = :icon, IP = :ip, NAME = :name, EINHEIT = :einheit,
									SAVE_DATA = :savedata, CHANNEL = :channel WHERE ID = :id;");
			}
			
			//DIY Sensor bearbeiten bzw. hinzufügen
			break;
		case "DIY Anwesenheitssensor":
			$paramArray = array("room" => $dataArray['room'], "name" => $dataArray['name'], "ip" => $dataArray['ip'],
			"icon" => $dataArray['icon'], "channel" => $dataArray['channel']);
			
			if($addNew){
				$query = $db->prepare("INSERT INTO 'DIY_PRESENCESENSORS' (RAUM, ICON, IP, NAME, CHANNEL)
									VALUES (:room, :icon, :ip, :name, :channel);");
			}	
			else{
				$query = $db->prepare("UPDATE 'DIY_PRESENCESENSORS' SET RAUM = :room, ICON = :icon, IP = :ip, NAME = :name, 
					CHANNEL = :channel WHERE ID = :id;");
			}
			
			//DIY Sensor bearbeiten bzw. hinzufügen
			break;
		case "DIY Schalter":
			$paramArray = array("room" => $dataArray['room'], "name" => $dataArray['name'], "ip" => $dataArray['ip'], "channel" => $dataArray['channel'],
				"icon" => $dataArray['icon']);
			
			if($addNew){
				$query = $db->prepare("INSERT INTO 'DIY_SENSORS' (RAUM, ICON, IP, NAME, CHANNEL)
									VALUES (:room, :icon, :ip, :name, :channel);");
			}	
			else{
				$query = $db->prepare("UPDATE 'DIY_SENSORS' SET RAUM = :room, ICON = :icon, IP = :ip, NAME = :name, CHANNEL = :channel
									WHERE ID = :id;");
			}
			
			//DIY Schalter bearbeiten bzw. hinzufügen
			break;
		case "DIY Gerät":
			$paramArray = array("room" => $dataArray['room'], "name" => $dataArray['name'], "ip" => $dataArray['ip'],
				"icon" => $dataArray['icon']);
			
			if($addNew){
				$query = $db->prepare("INSERT INTO 'DIY_DEVICES' (NAME, ROOM, IP, ICON) VALUES (:name, :room, :ip, :icon);");
			}	
			else{
				$query = $db->prepare("UPDATE 'DIY_DEVICES' SET ROOM = :room, ICON = :icon, IP = :ip, NAME = :name WHERE DEVICE = :id;");
			}
			
			//DIY Gerät bearbeiten bzw. hinzufügen
			break;
		//MAX! Thermostat
		case "MAX! Thermostat":
			$paramArray = array("room" => $dataArray['room'], "name" => $dataArray['name'], "icon" => $dataArray['icon']);
			
			if($addNew){
				$query = $db->prepare("INSERT INTO 'MAX_THERMOSTATS' (NAME, RAUM, ID, ICON) VALUES (:name, :room, :id, :icon);");
			}	
			else{
				$query = $db->prepare("UPDATE 'MAX_THERMOSTATS' SET RAUM = :room, ICON = :icon, NAME = :name WHERE ID = :id;");
			}
			
			//MAX! Thermostat bearbeiten bzw. hinzufügen
			break;
		//IP Kamera
		case "IP Kamera":
			$paramArray = array("room" => $dataArray['room'], "name" => $dataArray['name'], "icon" => $dataArray['icon']);
			
			if($addNew){
				$query = $db->prepare("INSERT INTO 'IP_CAMERA' (NAME, RAUM, ID, ICON) VALUES (:name, :room, :id, :icon);");
			}	
			else{
				$query = $db->prepare("UPDATE 'IP_CAMERAS'
				SET TYPE = :type, IP = :ip, PORT = :port , PATH = :path, USERNAME = :username, PASSWORD = :password,
				RECORD_FOOTAGE = :recordfootage , AUTO_DELETE = :autodelete, MOTION_DETECTION_THRESHOLD = :detectionthreshold,
				LOCATION = :room, ICON = :icon, NAME = :name WHERE ID = :id;");
			}
			
			//IP Kamera bearbeiten bzw. hinzufügen
			break;
		//Wake on Lan Gerät
		case "Wake on Lan Gerät":
			$paramArray = array("room" => $dataArray['room'], "name" => $dataArray['name'], "icon" => $dataArray['icon'], "mac" => $dataArray['mac']);
			
			//Wake on Lan Gerät bearbeiten bzw. hinzufügen
			if($addNew){
				$query = $db->prepare("INSERT INTO 'WAKE_ON_LAN' (DEVICE, NAME, LOCATION, ICON, MAC_ADDRESS) VALUES (null, :name, :room, :icon, :mac);");
			}
			else{
				$query = $db->prepare("UPDATE 'WAKE_ON_LAN' SET LOCATION = :room, ICON = :icon, NAME = :name, MAC_ADDRESS = :mac WHERE DEVICE = :id;");
			}
			
			break;
		//XBOX One
		case "XBOX One":
			$paramArray = array("room" => $dataArray['room'], "name" => $dataArray['name'], "icon" => $dataArray['icon'], "ip" => $dataArray['ip'],
			"liveid" => $dataArray['liveid']);
			
			//Wake on Lan Gerät bearbeiten bzw. hinzufügen
			if($addNew){
				$query = $db->prepare("INSERT INTO 'XBOX_ONE_WOL' (ID, NAME, LOCATION, ICON, IP_ADDRESS, XBOX_LIVE_ID) VALUES (null, :name, :room, :icon, :ip, :liveid);");
			}
			else{
				$query = $db->prepare("UPDATE 'XBOX_ONE_WOL' SET LOCATION = :room, ICON = :icon, NAME = :name, IP_ADDRESS = :ip, XBOX_LIVE_ID = :liveid WHERE DEVICE = :id;");
			}
			
			break;
		default:
			return "nosuchtype";
	}
}

function getDeviceData($type, $id, $db){
	if(!hasPermission("admin", $db)){
		return "noadmin";
	}
	
	$type = utf8_decode($type);
	
	//Räume abfragen
	$roomArray = array();
	
	foreach(getRooms($db)['rooms'] as $room){
		$roomArray[$room['location']] = $room['name'];
	}
	
	$queryParams = array("id" => $id);
	
	$devicedata = array();
	
	switch($type){
		//433 Mhz
		case "Funksteckdose":
			$dbQuery = $db->prepare("SELECT * FROM 'funksteckdosen' WHERE DEVICE == :id");
			$dbQuery->execute($queryParams);
			
			foreach($dbQuery->fetchAll(PDO::FETCH_ASSOC) as $query){
				$devicedata = array("room" => $roomArray[$query['ROOM']], "location" => $query['ROOM'], "name" => $query['NAME'], "hauscode" => $query['HAUSCODE'],
				"icon" => $query['ICON'], "steckdosennummer" => $query['STECKDOSENNUMMER']);
			}
			break;
			
		//DIY
		case "DIY Gerät":
			$dbQuery = $db->prepare("SELECT * FROM 'DIY_DEVICES' WHERE DEVICE == :id");
			$dbQuery->execute($queryParams);
			
			foreach($dbQuery->fetchAll(PDO::FETCH_ASSOC) as $query){
				$devicedata = array("room" => $roomArray[$query['ROOM']], "location" => $query['ROOM'], "name" => $query['NAME'],
				"ip" => $query['IP'],"icon" => $query['ICON']);
			}
			break;
		case "DIY Sensor":
			$dbQuery = $db->prepare("SELECT * FROM 'DIY_SENSORS' WHERE ID == :id");
			$dbQuery->execute($queryParams);
			
			foreach($dbQuery->fetchAll(PDO::FETCH_ASSOC) as $query){
				$devicedata = array("room" => $roomArray[$query['RAUM']], "location" => $query['RAUM'], "name" => $query['NAME'], "icon" => $query['ICON'],
				"ip" => $query['IP'], "save_data" => $query['SAVE_DATA'], "einheit" => $query['EINHEIT'], "channel" => $query['CHANNEL']);
			}
		case "DIY Fensterkontakt":
			$dbQuery = $db->prepare("SELECT * FROM 'DIY_REEDSENSORS' WHERE ID == :id");
			$dbQuery->execute($queryParams);
			
			foreach($dbQuery->fetchAll(PDO::FETCH_ASSOC) as $query){
				$devicedata = array("room" => $roomArray[$query['RAUM']], "location" => $query['RAUM'], "name" => $query['NAME'], "icon" => $query['ICON'],
				"ip" => $query['IP'], "channel" => $query['CHANNEL']);
			}
			break;
		case "DIY Anwesenheitssensor":
			$dbQuery = $db->prepare("SELECT * FROM 'DIY_PRESENCESENSORS' WHERE ID == :id");
			$dbQuery->execute($queryParams);
			
			foreach($dbQuery->fetchAll(PDO::FETCH_ASSOC) as $query){
				$devicedata = array("room" => $roomArray[$query['RAUM']], "location" => $query['RAUM'], "name" => $query['NAME'], "icon" => $query['ICON'],
				"ip" => $query['IP'], "channel" => $query['CHANNEL']);
			}
			break;
		case "DIY Schalter":
			$dbQuery = $db->prepare("SELECT * FROM 'DIY_SWITCHES' WHERE ID == :id");
			$dbQuery->execute($queryParams);
			
			foreach($dbQuery->fetchAll(PDO::FETCH_ASSOC) as $query){
				$devicedata = array("room" => $roomArray[$query['RAUM']], "location" => $query['RAUM'], "name" => $query['NAME'],
				"icon" => $query['ICON'], "ip" => $query['IP'], "channel" => $query['CHANNEL']);
			}
			break;
			
		//Z-Wave
		case "Z-Wave Sensor":
			$dbQuery = $db->prepare("SELECT * FROM 'ZWAVE_SENSOREN' WHERE ID == :id");
			$dbQuery->execute($queryParams);
			
			foreach($dbQuery->fetchAll(PDO::FETCH_ASSOC) as $query){
				$devicedata = array("room" => $roomArray[$query['RAUM']], "location" => $query['RAUM'], "name" => $query['SHORTFORM'],
				"icon" => $query['ICON'], "save_data" => $query['SAVE_DATA'], "einheit" => $query['EINHEIT']);
			}
			break;
		case "Z-Wave Thermostat":
			$dbQuery = $db->prepare("SELECT * FROM 'ZWAVE_THERMOSTATS' WHERE THERMOSTAT_ID == :id");
			$dbQuery->execute($queryParams);
			
			foreach($dbQuery->fetchAll(PDO::FETCH_ASSOC) as $query){
				$devicedata = array("room" => $roomArray[$query['RAUM']], "location" => $query['RAUM'], "name" => $query['NAME'], "icon" => $query['ICON']);
			}
			break;
		case "Z-Wave Strommesser":
			$dbQuery = $db->prepare("SELECT * FROM 'ZWAVE_POWER_METER' WHERE DEVICE_ID == :id");
			$dbQuery->execute($queryParams);
			
			foreach($dbQuery->fetchAll(PDO::FETCH_ASSOC) as $query){
				$devicedata = array("room" => $roomArray[$query['ROOM_ID']], "location" => $query['ROOM_ID'], "name" => $query['DEVICE_NAME'], "icon" => $query['ICON']);
			}
			break;
		case "Z-Wave Schalter":
			$dbQuery = $db->prepare("SELECT * FROM 'ZWAVE_SWITCHES' WHERE ID == :id");
			$dbQuery->execute($queryParams);
			
			foreach($dbQuery->fetchAll(PDO::FETCH_ASSOC) as $query){
				$devicedata = array("room" => $roomArray[$query['LOCATION']], "location" => $query['LOCATION'], "name" => $query['NAME'], "icon" => $query['ICON']);
			}
			break;
		case "Z-Wave Dimmer":
			$dbQuery = $db->prepare("SELECT * FROM 'ZWAVE_DIMMER' WHERE ID == :id");
			$dbQuery->execute($queryParams);
			
			foreach($dbQuery->fetchAll(PDO::FETCH_ASSOC) as $query){
				$devicedata = array("room" => $roomArray[$query['LOCATION']], "location" => $query['LOCATION'], "name" => $query['NAME'], "icon" => $query['ICON']);
			}
			break;
		//MAX! Thermostat
		case "MAX! Thermostat":
			$dbQuery = $db->prepare("SELECT * FROM 'MAX_THERMOSTATS' WHERE ID == :id");
			$dbQuery->execute($queryParams);
			
			foreach($dbQuery->fetchAll(PDO::FETCH_ASSOC) as $query){
				$devicedata = array("room" => $roomArray[$query['RAUM']], "location" => $query['RAUM'], "name" => $query['NAME'], "icon" => $query['ICON']);
			}
			break;
		//IP Kamera
		case "IP Kamera":
			$dbQuery = $db->prepare("SELECT * FROM 'IP_CAMERA' WHERE ID == :id");
			$dbQuery->execute($queryParams);
			
			foreach($dbQuery->fetchAll(PDO::FETCH_ASSOC) as $query){
				$devicedata = array("room" => $roomArray[$query['LOCATION']], "location" => $query['RAUM'], "name" => $query['NAME'],
				"icon" => $query['ICON'], "ip" => $query['IP'], "port" => $query['PORT'], "path" => $query['PATH'],
				"username" => $query['USERNAME'], "password" => $query['PASSWORD'], "recordfootage" => $query['RECORD_FOOTAGE'],
				"autodelete" => $query['AUTO_DELETE'], "detectionthreshold" => $query['MOTION_DETECTION_THRESHOLD']);
			}
			break;
		//Wake on Lan Gerät
		case "Wake on Lan Gerät":
			$dbQuery = $db->prepare("SELECT * FROM 'WAKE_ON_LAN' WHERE DEVICE == :id");
			$dbQuery->execute($queryParams);
			
			foreach($dbQuery->fetchAll(PDO::FETCH_ASSOC) as $query){
				$devicedata = array("room" => $roomArray[$query['LOCATION']], "location" => $query['LOCATION'], "name" => $query['NAME'],
				"icon" => $query['ICON'], "mac" => $query['MAC_ADDRESS']);
			}
			break;
		//XBOX One
		case "XBOX One":
			$dbQuery = $db->prepare("SELECT * FROM 'XBOX_ONE_WOL' WHERE ID == :id");
			$dbQuery->execute($queryParams);
			
			foreach($dbQuery->fetchAll(PDO::FETCH_ASSOC) as $query){
				$devicedata = array("room" => $roomArray[$query['LOCATION']], "location" => $query['LOCATION'], "name" => $query['NAME'],
				"icon" => $query['ICON'], "ip" => $query['IP_ADDRESS'], "liveid" => $query['XBOX_LIVE_ID']);
			}
			break;
		default:
			return "nosuchtype";
	}
	
	return array("devicedata" => $devicedata);
}

function deleteDevice($type, $devicekey, $db){
	if(!hasPermission("admin", $db)){
		return "noadmin";
	}
	
	$type = utf8_decode($type);
	
	switch($type){
		//433 Mhz
		case "Funksteckdose":
			$result = $db->prepare("DELETE FROM funksteckdosen WHERE DEVICE == :device");
			break;
		//DIY
		case "DIY Gerät":
			$result = $db->prepare("DELETE FROM DIY_DEVICES WHERE DEVICE == :device");
			break;
		case "DIY Fensterkontakt":
			$result = $db->prepare("DELETE FROM DIY_REEDSENSORS WHERE ID == :device");
			break;
		case "DIY Sensor":
			$result = $db->prepare("DELETE FROM DIY_SENSORS WHERE ID == :device");
			break;
		case "DIY Schalter":
			$result = $db->prepare("DELETE FROM DIY_SWITCHES WHERE ID == :device");
			break;
		//Z-Wave
		case "Z-Wave Sensor":
			$result = $db->prepare("DELETE FROM ZWAVE_SENSOREN WHERE ID == :device");
			break;
		case "Z-Wave Thermostat":
			$result = $db->prepare("DELETE FROM ZWAVE_THERMOSTATS WHERE THERMOSTAT_ID == :device");
			break;
		case "Z-Wave Stromzähler":
			$result = $db->prepare("DELETE FROM ZWAVE_POWER_METER WHERE DEVICE_ID == :device");
			break;
		case "Z-Wave Dimmer":
			$result = $db->prepare("DELETE FROM ZWAVE_DIMMER WHERE ID == :device");
			break;
		case "Z-Wave Schalter":
			$result = $db->prepare("DELETE FROM ZWAVE_SWITCHES WHERE ID == :device");
			break;
		case "Wake on Lan Gerät":
			$result = $db->prepare("DELETE FROM WAKE_ON_LAN WHERE DEVICE == :device");
			break;
		case "XBOX One":
			$result = $db->prepare("DELETE FROM XBOX_ONE_WOL WHERE ID == :device");
			break;
		default:
		return "nosuchtype";
	}
	
	$result->execute(array("device" => $devicekey));
	
	if($result == true) return "ok";
	else return "error";
}
'''

def get_device_data(username, type, id, db):
    if not has_permission(username, "admin", db):
        return {'result': 'noadmin'}

    room_array = {}

    for room in get_rooms(username, db)['rooms']:
        room_array[room['location']] = room['name']

    print(room_array)

    with db:
        cur = db.cursor()

        param_array = {'id': id}

        device_data = {}

        #Funksteckdose
        if type == FUNKSTECKDOSE:
            cur.execute("SELECT * FROM FUNKSTECKDOSEN WHERE DEVICE = :id", param_array)

            data = cur.fetchone()

            device_data = {'room': room_array[int(data['ROOM'])], 'location': data['ROOM'], 'name': data['NAME'],
                           'hauscode': data['HAUSCODE'], 'icon': data['ICON'], 'steckdosennummer': data['STECKDOSENNUMMER']}
        #Z-Wave
        elif type == ZWAVE_POWER_METER:
            cur.execute("SELECT * FROM ZWAVE_POWER_METER WHERE DEVICE_ID = :id", param_array)

            data = cur.fetchone()

            device_data = {'room': room_array[int(data['ROOM_ID'])], 'location': data['ROOM_ID'], 'name': data['DEVICE_NAME'],
                           'is_reset_daily': (data['IS_RESET_DAILY']==1), 'icon': data['ICON']}
        elif type == ZWAVE_SENSOR:
            cur.execute("SELECT * FROM ZWAVE_SENSOREN WHERE ID = :id", param_array)

            data = cur.fetchone()

            device_data = {'room': room_array[int(data['RAUM'])], 'location': data['RAUM'], 'name': data['SHORTFORM'],
                           'save_data': data['SAVE_DATA'], 'icon': data['ICON'],
                           'sensor_type': data['SENSOR_TYPE'], 'sensor_type_name': SENSOR_TYPE_MAP[data['SENSOR_TYPE']]['name']}
        elif type == ZWAVE_THERMOSTAT:
            cur.execute("SELECT * FROM ZWAVE_THERMOSTATS WHERE THERMOSTAT_ID = :id", param_array)

            data = cur.fetchone()

            device_data = {'room': room_array[int(data['RAUM'])], 'location': data['RAUM'], 'name': data['NAME'],
                           'icon': data['ICON']}
        elif type == ZWAVE_SWITCH:
            cur.execute("SELECT * FROM ZWAVE_SWITCHES WHERE ID = :id", param_array)

            data = cur.fetchone()

            device_data = {'room': room_array[int(data['LOCATION'])], 'location': data['LOCATION'], 'name': data['NAME'],
                           'icon': data['ICON']}
        elif type == ZWAVE_DIMMER:
            cur.execute("SELECT * FROM ZWAVE_DIMMER WHERE ID = :id", param_array)

            data = cur.fetchone()

            device_data = {'room': room_array[int(data['LOCATION'])], 'location': data['LOCATION'], 'name': data['NAME'],
                           'icon': data['ICON']}
        #MQTT-Sensor
        elif type == MQTT_SENSOR:
            cur.execute("SELECT * FROM MQTT_SENSORS WHERE ID = :id", param_array)

            data = cur.fetchone()

            device_data = {'room': room_array[int(data['ROOM'])], 'location': data['ROOM'], 'name': data['NAME'], 'icon': data['ICON'],
                           'topic': data['TOPIC'], 'key': data['KEY'], 'sensor_type': data['TYPE'],
                           'sensor_type_name': SENSOR_TYPE_MAP[data['TYPE']]['name'], 'save_data': data['SAVE_DATA']}
        #IP Kamera
        elif type == IP_CAM:
            cur.execute("SELECT * FROM ZWAVE_DIMMER WHERE ID = :id", param_array)

            data = cur.fetchone()

            device_data = {'room': room_array[int(data['LOCATION'])], 'location': data['LOCATION'], 'name': data['NAME'],
                           'icon': data['ICON'], 'ip': data['IP'], 'port': data['PORT'], 'path': data['PATH'],
                           'username': data['USERNAME'], 'password': data['PASSWORD'], 'recordfootage': data['RECORD_FOOTAGE'],
                           'autodelete': data['AUTO_DELETE'], 'detectionthreshold': data['MOTION_DETECTION_THRESHOLD']}
        #URL-Toggle
        elif type == URL_TOGGLE:
            cur.execute("SELECT * FROM URL_TOGGLE WHERE ID = :id", param_array)

            data = cur.fetchone()
            device_data = {'room': room_array[int(data['LOCATION'])], 'location': data['LOCATION'], 'name': data['NAME'],
                           'icon': data['ICON'], 'toggle_url': data['TOGGLE_URL']}
        #URL-Switch
        elif type == URL_SWITCH:
            cur.execute("SELECT * FROM URL_SWITCH_BINARY WHERE ID = :id", param_array)

            data = cur.fetchone()
            device_data = {'room': room_array[int(data['LOCATION'])], 'location': data['LOCATION'], 'name': data['NAME'],
                           'icon': data['ICON'], 'on_url': data['URL_ON'], 'off_url': data['URL_OFF'],
                           'get_state_url': data['URL_GET_STATE']}
        #URL RGB-Licht
        elif type == URL_RGB_LIGHT:
            cur.execute("SELECT * FROM URL_RGB_LIGHT WHERE ID = :id", param_array)

            data = cur.fetchone()
            device_data = {'room': room_array[int(data['LOCATION'])], 'location': data['LOCATION'], 'name': data['NAME'],
                           'icon': data['ICON'], 'url': data['URL']}
        #Philips Hue RGB-Licht
        elif type == PHILIPS_HUE_LIGHT:
            cur.execute("SELECT * FROM PHILIPS_HUE_LIGHTS WHERE ID = :id", param_array)

            data = cur.fetchone()
            device_data = {'room': room_array[int(data['LOCATION'])], 'location': data['LOCATION'], 'name': data['NAME'],
                           'icon': data['ICON'], 'type': data['TYPE']}
        #MAX Thermostat
        elif type == MAX_THERMOSTAT:
            cur.execute("SELECT * FROM MAX_THERMOSTATS WHERE ID = :id", param_array)

            data = cur.fetchone()
            device_data = {'room': room_array[int(data['RAUM'])], 'location': data['RAUM'], 'name': data['NAME'],
                           'icon': data['ICON']}
        #Rademacher
        elif type == RADEMACHER_THERMOSTAT:
            cur.execute("SELECT * FROM HOMEPILOT_THERMOSTATS WHERE ID = :id", param_array)

            data = cur.fetchone()
            device_data = {'room': room_array[int(data['ROOM'])], 'location': data['ROOM'], 'name': data['NAME'],
                           'icon': data['ICON']}
        elif type == RADEMACHER_BLIND_CONTROL:
            cur.execute("SELECT * FROM HOMEPILOT_THERMOSTATS WHERE ID = :id", param_array)

            data = cur.fetchone()
            device_data = {'room': room_array[int(data['LOCATION'])], 'location': data['LOCATION'], 'name': data['NAME'],
                           'icon': data['ICON']}
        else:
            return {'result': 'nosuchtype'}

        return {'devicedata': device_data}