#!/usr/bin/python
# -*- coding: utf-8 -*-

from homevee.DeviceAPI.zwave.get_devices import get_device_value
from homevee.device_types import *
from homevee.Helper.permissions import has_permission

SENSOR_TYPE_MAP = {
	'temp': {'name': 'Temperatur', 'einheit': '°C', 'einheit_word': 'Grad'},
	'hygro': {'name': 'Luftfeuchtigkeit', 'einheit': '%', 'einheit_word': '%'},
	'helligkeit': {'name': 'Helligkeit', 'einheit': 'Lux', 'einheit_word': 'Lumen'},
	'uv': {'name': 'UV-Licht', 'einheit': 'UV-Index', 'einheit_word': 'UV-Index'},
	'powermeter': {'name': 'Stromverbrauch', 'einheit': 'Watt', 'einheit_word': 'Watt'},
}

#def get_sensor_types():
#    return SENSOR_TYPE_MAP

def get_einheit(type, id, db):
	with db:
		cur = db.cursor()
		db_data = {
			ZWAVE_SENSOR: {'table': 'ZWAVE_SENSOREN', 'sensor_type_col': 'SENSOR_TYPE', 'id_col': 'ID'},
			MQTT_SENSOR: {'table': 'MQTT_SENSORS', 'sensor_type_col': 'TYPE', 'id_col': 'ID'}
		}

		cur.execute("SELECT "+db_data[type]['sensor_type_col']+" FROM "+db_data[type]['table']+" WHERE "+db_data[type]['id_col']+" = :id",
					{'id': id})

		return SENSOR_TYPE_MAP[cur.fetchone()[db_data[type]['sensor_type_col']]]['einheit']

def get_sensor_value(type, id, show_einheit, db):
	if type == ZWAVE_SENSOR:
		if id is not None:
			value = get_device_value(type, id, db)

			try:
				output = round(float(value), 1)

				if show_einheit:
					output = str(output) + " " + get_einheit(type, id, db)
			except:
				output = "N/A"

			return output
	elif type == MQTT_SENSOR:
		if id is not None:
			with db:
				cur = db.cursor()
				cur.execute("SELECT * FROM MQTT_SENSORS WHERE ID == :id",
							{'id': id})

				data = cur.fetchone()

				value = data['LAST_VALUE']

				try:
					output = round(float(value), 1)
					if show_einheit:
						output = str(output) + " " + get_einheit(type, id, db)
				except:
					output = "N/A"

				return output
	# Andere Typen hinzufügen

def get_sensor_data(username, room, type, id, show_einheit, db):
	if not has_permission(username, room, db):
		return {'status': 'nopermission'}

	if type is not None and type != "" and id is not None and id != "":
		return get_sensor_value(type, id, show_einheit, db)
	else:
		with db:
			cur = db.cursor()

			#Räume laden
			if room == "all":
				cur.execute("SELECT * FROM ROOMS")
			else:
				cur.execute("SELECT * FROM ROOMS WHERE LOCATION == :room",
					{'room': room})

			values = []

			for room in cur.fetchall():
				value_array = []

				if not has_permission(username, room['LOCATION'], db):
					continue
					#return "nopermission"

				#Alle Z-Wave Sensoren
				type = ZWAVE_SENSOR
				cur.execute("SELECT * FROM ZWAVE_SENSOREN WHERE RAUM == :location",{'location': room['LOCATION']})

				for sensor in cur.fetchall():
					value = {'shortform': sensor['SHORTFORM'], 'id': sensor['ID'], 'device_type': type, 'icon': sensor['ICON'],
						'wert': get_sensor_data(username, room['LOCATION'], type, sensor['ID'], 1, db)}
					value_array.append(value)

				#Alle MQTT Sensoren
				type = MQTT_SENSOR
				cur.execute("SELECT * FROM MQTT_SENSORS WHERE ROOM == :location",{'location': room['LOCATION']})

				for sensor in cur.fetchall():
					value = {'shortform': sensor['NAME'], 'id': sensor['ID'], 'device_type': type, 'icon': sensor['ICON'],
						'wert': get_sensor_data(username, room['LOCATION'], type, sensor['ID'], 1, db)}
					value_array.append(value)

				#Alle anderen Sensoren

				value_item = {'name': room['NAME'], 'location': room['LOCATION'], 'icon': room['ICON'], 'value_array': value_array}

				values.append(value_item)

			cur.close()

			return {'values': values}

