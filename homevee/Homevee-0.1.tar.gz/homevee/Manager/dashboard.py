#!/usr/bin/python
# -*- coding: utf-8 -*-
import datetime
import json

from homevee.DeviceAPI.heating import get_thermostats
from homevee.Functions.calendar import get_calendar_day_items
from homevee.Functions.nutrition_data import get_user_nutrition_overview
from homevee.Functions.room_data import get_rooms, get_room_name
from homevee.Functions.sensor_data import get_sensor_data
from homevee.Functions.weather import get_weather
from homevee.Helper.helper_functions import has_permission
from homevee.device_types import *

STATIC_DASHBOARD_ITEMS = ['calendar', 'weather', 'tvprogramme', 'drivingtime', 'nutritionmanager']

def get_user_dashboard(username, db):
    with db:
        cur = db.cursor()

        cur.execute("SELECT * FROM userdata WHERE USERNAME == :username",
                    {'username': username})

        data = cur.fetchone()

        user_dashboard = data['DASHBOARD_DATA']

        if user_dashboard is None:
            data = {'static': [], 'dynamic': []}
        else:
            data = json.loads(user_dashboard)

        dashboard_data = {}
        dashboard_data['static'] = data['static']

        if dashboard_data is not None and dashboard_data != "":

            dashboard_keys = []
            for item in dashboard_data['static']:
                print item
                dashboard_keys.append(item['id'])


            for item in STATIC_DASHBOARD_ITEMS:
                if item not in dashboard_keys:
                    print item+" not existing"
                    dashboard_data['static'].append({'id': item, 'checked': False})

            dashboard_data['dynamic'] = []

            '''
            dynamic_temp_items = data['dynamic']
            devices_map = {}
            dynamic_items = []

            print dynamic_temp_items

            for item in dynamic_temp_items:
                found = False

                if(item['type'] not in devices_map):
                    devices_map[item['type']] = []

                if item['id'] not in devices_map[item['type']]:
                    devices_map[item['type']].append(item['id'])
                else:
                    found = True

                if not found:
                    dynamic_items.append(item)

            print dynamic_items
            '''

            devices_map = {}
            for item in data['dynamic']:
                found = False

                if (item['type'] not in devices_map):
                    devices_map[item['type']] = []

                if item['id'] not in devices_map[item['type']]:
                    devices_map[item['type']].append(item['id'])
                else:
                    found = True

                if not found:
                    dashboard_data['dynamic'].append(get_device_info(username, item['type'], item['id'], db))

            return dashboard_data

    return {'result': 'unknownuser'}

def get_user_dashboard_items(username, db):
    dashboard_array = []

    with db:
        cur = db.cursor()

        cur.execute("SELECT * FROM USERDATA WHERE USERNAME == :username", {'username': username})

        db_data = cur.fetchone()

        if db_data is not None:
            data = db_data['DASHBOARD_DATA']

            if data is None:
                return {'dashboard': dashboard_array}

            data = json.loads(data)

            static_items = data['static']

            static_data = {}

            for item in static_items:
                static_data[item['id']] = item['checked']

            dynamic_temp_items = data['dynamic']
            devices_map = {}
            dynamic_items = []

            print dynamic_temp_items

            for item in dynamic_temp_items:
                found = False

                if(item['type'] not in devices_map):
                    devices_map[item['type']] = []

                if item['id'] not in devices_map[item['type']]:
                    devices_map[item['type']].append(item['id'])
                else:
                    found = True

                if not found:
                    dynamic_items.append(item)

            print dynamic_items

            # Wetter hinzufügen
            if 'weather' in static_data:
                if static_data['weather']:
                    weather_data = get_weather(1, db)
                    dashboard_array.append({'id': 'weather', 'data': weather_data[0]})

            # TV Programm hinzufügen
            if 'tvprogramme' in static_data:
                if static_data['tvprogramme']:
                    dashboard_array.append({'id': 'tvprogramme', 'data': None})

            #Kalender hinzufügen
            if 'calendar' in static_data:
                if static_data['calendar']:
                    calendar_entries = get_calendar_day_items(username, datetime.datetime.now().strftime("%Y-%m-%d"), db)

                    items = calendar_entries['calendar_entries']

                    data = None
                    for item in items:
                        start = datetime.datetime.strptime(item['start'], '%H:%M')
                        dnow = datetime.datetime.now()

                        if(dnow.time() > start.time()):
                            continue

                        if data is None:
                            data = item['name'] + " um " + item['start']
                        else:
                            data += '\n' + item['name'] + " um " + item['start']+ " Uhr"

                    if data is None:
                        data = 'Keine Termine heute'

                    dashboard_array.append({'id': 'calendar', 'data': data})

            # Fahrzeit
            if 'drivingtime' in static_data:
                if static_data['drivingtime']:
                    dashboard_array.append({'id': 'drivingtime', 'data': '27 min'})

            # Ernährungsmanager
            if 'nutritionmanager' in static_data:
                if static_data['nutritionmanager']:
                    calories_left = get_user_nutrition_overview(username, db)['data']['nutrition_day_data']['calories_left']

                    if(calories_left >= 0):
                        text = str(calories_left)+' Kalorien übrig'
                    else:
                        text = str(calories_left)+' Kalorien über deinem Ziel'

                    dashboard_array.append({'id': 'nutritionmanager', 'data': text})

            if len(dynamic_items) > 0:
                dashboard_array.append({'id': 'favouritedevices', 'data': None})

        return {'dashboard': dashboard_array}

def edit_user_dashboard(username, dashboard_data, db):
    with db:
        cur = db.cursor()

        dashboard_data = json.loads(dashboard_data)

        #Check duplicates

        dynamic_temp_items = dashboard_data['dynamic']
        devices_map = {}
        dynamic_items = []

        print dynamic_temp_items

        for item in dynamic_temp_items:
            found = False

            if (item['type'] not in devices_map):
                devices_map[item['type']] = []

            if item['id'] not in devices_map[item['type']]:
                devices_map[item['type']].append(item['id'])
            else:
                found = True

            if not found:
                dynamic_items.append(item)

        print dynamic_items

        dashboard_data['dynamic'] = dynamic_items

        #Check duplicates end

        dashboard_data_json = json.dumps(dashboard_data)

        cur.execute("UPDATE USERDATA SET DASHBOARD_DATA = :data WHERE USERNAME == :username",
                    {'data': dashboard_data_json, 'username': username})

        cur.close()

        return get_user_dashboard(username, db)

def get_user_favourite_devices(username, db):
    with db:
        cur = db.cursor()

        cur.execute("SELECT * FROM USERDATA WHERE USERNAME == :username", {'username': username})

        data = json.loads(cur.fetchone()['DASHBOARD_DATA'])

        dynamic_items = data['dynamic']

        print "data: "+str(data)

        fav_array = get_dynamic_items(username, dynamic_items, db)

        return fav_array

def get_dynamic_items(username, dynamic_items, db):
    rooms = get_rooms(username, db)['rooms']

    favourites = {}

    room_map = {}

    for room in rooms:
        favourites[int(room['location'])] = []
        room_map[room['location']] = room

    types = {}

    for item in dynamic_items:
        #print item
        if item['type'] not in types:
            types[item['type']] = []

        types[item['type']].append(item['id'])
        print types

    for type in types:
        ids = types[type]
        if len(ids) > 0:
            for id in ids:
                item = get_device_info(username, type, id, db)

                if item is None:
                    continue

                print favourites

                favourites[int(item['room'])].append(item)

    output = []
    for location in favourites.keys():
        room_item = room_map[location]

        if len(favourites[location]) > 0:
            room_item['devices'] = favourites[location]
            output.append(room_item)

    return output

def get_device_info(username, type, id, db):

    print type + " - " + id

    with db:
        cur = db.cursor()

        device_data = None

        try:
            if type == FUNKSTECKDOSE:
                cur.execute("SELECT * FROM FUNKSTECKDOSEN WHERE DEVICE == :id", {'id': id})
                item = cur.fetchone()
                device_data = {'room': item['ROOM'], 'name': item['NAME'], 'icon': item['ICON'],
                               'value': item['ZUSTAND'] == "1",
                               'type': 'switch', 'devicetype': type, 'id': id}
            elif type == PHILIPS_HUE_LIGHT:
                cur.execute("SELECT * FROM PHILIPS_HUE_LIGHTS WHERE ID == :id", {'id': id})
                item = cur.fetchone()
                device_data = {'room': item['LOCATION'], 'name': item['NAME'],
                               'icon': item['ICON'],
                               'value': {'is_on': False, 'brightness': 100, 'color': item['HUE']},
                               'type': 'rgb', 'devicetype': type, 'id': id}
            #URL-Geräte
            elif type == URL_RGB_LIGHT:
                cur.execute("SELECT * FROM URL_RGB_LIGHT WHERE ID = :id", {'id': id})
                item = cur.fetchone()
                device_data = {'name': item['NAME'], 'room': item['LOCATION'], 'id': item['ID'], 'type': 'rgb',
                               'icon': item['ICON'], 'value': {'is_on': False, 'brightness': 100, 'color': item['LAST_COLOR']}}
            elif type == URL_TOGGLE:
                cur.execute("SELECT * FROM URL_TOGGLE WHERE ID = :id",{'id': id})
                item = cur.fetchone()
                device_data = {'name': item['NAME'], 'room': item['LOCATION'], 'id': item['ID'],
                                    'icon': item['ICON'], 'value': '', 'type': 'toggle'}
            #Z-Wave
            elif type == ZWAVE_THERMOSTAT:
                cur.execute("SELECT * FROM ZWAVE_THERMOSTATS WHERE THERMOSTAT_ID == :id", {'id': id})
                item = cur.fetchone()
                data = get_thermostats(username, item['RAUM'], type, item['THERMOSTAT_ID'], db)
                device_data = {'name': item['NAME'], 'id': item['THERMOSTAT_ID'],
                        'icon': item['ICON'], 'room': item['RAUM'], 'type': 'heating',
                        'value': data['value'], 'min': data['min'], 'max': data['max'], 'step': 0.5}
            elif type == ZWAVE_DIMMER:
                cur.execute("SELECT * FROM ZWAVE_DIMMER WHERE ID == :id", {'id': id})
                item = cur.fetchone()
                device_data = {'name': item['NAME'], 'id': item['THERMOSTAT_ID'],
                        'icon': item['ICON'], 'room': item['LOCATION'], 'type': 'heating',
                        'value': item['VALUE']}
            elif type == ZWAVE_POWER_METER:
                cur.execute("SELECT * FROM ZWAVE_THERMOSTATS WHERE DEVICE_ID == :id", {'id': id})
                item = cur.fetchone()
                device_data = {'name': item['NAME'], 'id': item['DEVICE_ID'],
                        'icon': item['ICON'], 'room': item['LOCATION'], 'type': 'heating',
                        'value': item['VALUE']}
            elif type == ZWAVE_SENSOR:
                cur.execute("SELECT * FROM ZWAVE_SENSOREN WHERE ID == :id", {'id': id})
                item = cur.fetchone()
                device_data = {'name': item['SHORTFORM'], 'id': item['ID'],
                        'icon': item['ICON'], 'room': item['RAUM'], 'type': 'value',
                               'value': get_sensor_data(username, item['RAUM'], type, id, 1, db)}
            elif type == ZWAVE_SWITCH:
                cur.execute("SELECT * FROM ZWAVE_SWITCHES WHERE THERMOSTAT_ID == :id", {'id': id})
                item = cur.fetchone()
                device_data = {'name': item['NAME'], 'id': item['THERMOSTAT_ID'],
                        'icon': item['ICON'], 'room': item['LOCATION'], 'type': 'heating',
                        'value': item['VALUE']}
            #MAX Cube
            elif type == MAX_THERMOSTAT:
                cur.execute("SELECT * FROM MAX_THERMOSTATS WHERE ID == :id", {'id': id})
                item = cur.fetchone()
                data = get_thermostats(username, item['RAUM'], type, id, db)
                device_data = {'name': item['NAME'], 'id': item['ID'], 'room': item['RAUM'], 'type': 'heating',
                        'icon': item['ICON'],
                        'value': data['value'], 'min': data['min'], 'max': data['max'], 'step': 0.5}
            #Wake on Lan
            elif type == WAKE_ON_LAN:
                cur.execute("SELECT * FROM WAKE_ON_LAN WHERE DEVICE == :id", {'id': id})
                item = cur.fetchone()
                device_data = {'name': item['NAME'], 'id': item['DEVICE'], 'icon': item['ICON'], 'room': item['LOCATION'],
                               'value': '', 'type': 'wakeonlan'}
            elif type == XBOX_ONE_WOL:
                cur.execute("SELECT * FROM XBOX_ONE_WOL WHERE ID == :id", {'id': id})
                item = cur.fetchone()
                device_data = {'name': item['NAME'], 'id': item['ID'], 'icon': item['ICON'], 'room': item['LOCATION'],
                               'value': '', 'type': 'wakeonlan'}

            #MQTT Sensor
            elif type == MQTT_SENSOR:
                cur.execute("SELECT * FROM MQTT_SENSORS WHERE ID == :id", {'id': id})
                item = cur.fetchone()
                device_data = {'name': item['NAME'], 'id': item['ID'],
                               'icon': item['ICON'], 'room': item['ROOM'], 'type': 'value',
                               'value': get_sensor_data(username, item['ROOM'], type, id, 1, db)}
        except:
            print "Error loading device"

        if device_data is None or not has_permission(username, device_data['room'], db):
            return None

        device_data['roomname'] = get_room_name(device_data['room'], db)
        device_data['devicetype'] = type

        return device_data

    '''//DIY
		case "DIY Gerät":
			$dbQuery = $db->prepare("SELECT * FROM 'DIY_DEVICES' WHERE DEVICE == :id");
			$dbQuery->execute($queryParams);
			
			
			$query = $dbQuery->fetch(PDO::FETCH_ASSOC);
			$devicedata = array("room" => $query['ROOM'], "name" => $query['NAME'], "icon" => $query['ICON'],
			"value" => "", "type" => "button");
			break;
		case "DIY Sensor":
			$dbQuery = $db->prepare("SELECT * FROM 'DIY_SENSORS' WHERE ID == :id");
			$dbQuery->execute($queryParams);
			
			
			$query = $dbQuery->fetch(PDO::FETCH_ASSOC);
			$devicedata = array("room" => $query['RAUM'], "name" => $query['NAME'], "icon" => $query['ICON'],
			"value" => getSensorData($query['RAUM'], $type, $id, "1", $db), "type" => "value");
		case "DIY Fensterkontakt":
			$dbQuery = $db->prepare("SELECT * FROM 'DIY_REEDSENSORS' WHERE ID == :id");
			$dbQuery->execute($queryParams);
			
			
			$query = $dbQuery->fetch(PDO::FETCH_ASSOC);
			$devicedata = array("room" => $query['RAUM'], "name" => $query['NAME'], "icon" => $query['ICON'],
			"value" => getReedData($query['RAUM'], $type, $id, $db), "type" => "reed");
			break;
		case "DIY Anwesenheitssensor":
			$dbQuery = $db->prepare("SELECT * FROM 'DIY_PRESENCESENSORS' WHERE ID == :id");
			$dbQuery->execute($queryParams);
			
			
			$query = $dbQuery->fetch(PDO::FETCH_ASSOC);
			$devicedata = array("room" => $query['RAUM'], "name" => $query['NAME'], "icon" => $query['ICON'],
			"value" => getReedData($query['RAUM'], $type, $id, $db), "type" => "presence");
			break;
		case "DIY Schalter":
			$dbQuery = $db->prepare("SELECT * FROM 'DIY_SWITCHES' WHERE ID == :id");
			$dbQuery->execute($queryParams);
			
			
			$query = $dbQuery->fetch(PDO::FETCH_ASSOC);
			$devicedata = array("room" => $query['RAUM'], "name" => $query['NAME'], "icon" => $query['ICON'],
			"value" => getModes($query['RAUM'], $type, $id, $db) === "1", "type" => "switch");
			break;
		case "IP Kamera":
			$dbQuery = $db->prepare("SELECT * FROM 'IP_CAMERA' WHERE ID == :id");
			$dbQuery->execute($queryParams);
			
			$query = $dbQuery->fetch(PDO::FETCH_ASSOC);
			
			$ip = $query['IP'];
			$port = $query['PORT'];
				
			if($port != null && $port != ""){
				$port = ":$port";
			}
				
			$path = $query['PATH'];
				
			$url = "http://$ip$port$path";
			
			$devicedata = array('room' => $query['LOCATION'], 'name' => $query['NAME'], 'icon' => $query['ICON'],
			'value' => "", 'url' => $url, 'username' => $query['USERNAME'], 'password' => $query['PASSWORD'],
			'type' => "ipcamera");
			break;
			
		default:
			return null;
	}
	
	if(!hasPermission($devicedata['room'], $db) || $devicedata['room'] == null){
		return null;
	}
	else{
		$devicedata['roomname'] = $roomArray[$devicedata['room']];
		$devicedata['devicetype'] = $type;
		$devicedata['id'] = $id;
		
		return $devicedata;
	}
}
?>
    '''
