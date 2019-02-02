#!/usr/bin/python
# -*- coding: utf-8 -*-
import datetime

from homevee.Functions.sensor_data import get_sensor_value
from homevee.VoiceAssistant import helper


def conditions_true(condition_data, db):
    #Format: {'and':[{'and':[{'action':'time', 'comparator':'greater', 'value':'08:00'}, {'action':'time', 'comparator':'less', 'value':'20:00'}]},
    # {'and':[{}, {}]}]}

    if('and' in condition_data):
        for condition in condition_data['and']:
            if not conditions_true(condition, db):
                return False
            return True
    if(isinstance(condition_data, list)):
        if(len(condition_data) == 0):
            return True
        for condition in condition_data:
            if not conditions_true(condition, db):
                return False
            return True
    elif('or' in condition_data):
        for condition in condition_data['or']:
            if conditions_true(condition, db):
                return True
        return False
    else:
        #check single conditions
        return check_single_condition(condition_data, db)

def check_single_condition(condition_data, db):
    #{'action': 'timeperiod', 'from': '08:00', 'to': '20:00'}
    if(condition_data['type'] == "timeperiod"):
        return is_in_time_period(condition_data)
    #{'action': 'weekdays', 'days': [5, 6]}
    elif(condition_data['type'] == "weekdays"):
        return datetime.datetime.today().weekday() in condition_data['days']
    #{'action': 'sensor_value', 'type': 'MQTT Sensor', 'id': '1', 'comparator': '>', 'value': 28}
    elif(condition_data['type'] == "sensorvalue"):
        value = get_sensor_value(condition_data['devicetype'], condition_data['deviceid'], False, db)
        print value
        return check_value(condition_data['comparator'], value, condition_data['value'])
    #{'action': 'user_at_home', 'user': 'sascha', 'at_home': False}
    elif(condition_data['type'] == "user_at_home"):
        if(condition_data['at_home']):
            return helper.user_is_at_home(condition_data['username'], db)
        elif(not condition_data['at_home']):
            return not helper.user_is_at_home(condition_data['username'], db)
    return False

def check_value(comparator, is_value, value_condition):
    if(comparator == ">"):
        return float(is_value) > float(value_condition)
    elif(comparator == ">="):
        return float(is_value) >= float(value_condition)
    elif(comparator == "<"):
        return float(is_value) < float(value_condition)
    elif(comparator == "<="):
        return float(is_value) <= float(value_condition)
    elif(comparator == "=="):
        return float(is_value) == float(value_condition)
    elif(comparator == "!="):
        return float(is_value) != float(value_condition)

def is_in_time_period(condition_data):
    today = datetime.datetime.today()

    from_hour, from_minute = condition_data['from'].split(":")

    to_hour, to_minute = condition_data['to'].split(":")

    from_hour = int(from_hour)
    from_minute = int(from_minute)
    to_hour = int(to_hour)
    to_minute = int(to_minute)

    if (today.hour == from_hour):
        if (today.minute >= from_minute):
            if (today.hour == to_hour):
                if (today.minute <= to_minute):
                    return True
            elif (today.hour < to_hour):
                return True
    elif (today.hour >= from_hour):
        if (today.hour == to_hour):
            if (today.minute <= to_minute):
                return True
        elif (today.hour < to_hour):
            return True
    else:
        return False