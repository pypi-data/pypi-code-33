#!/usr/bin/python
# -*- coding: utf-8 -*-
import json

from homevee.Functions.room_data import get_room_name
from homevee.Helper.helper_functions import has_permission


def get_automations(username, room, db):
    if not has_permission(username, room, db):
        return {'result': 'nopermission'}

    rules = []

    with db:
        cur = db.cursor()

        cur.execute("SELECT * FROM AUTOMATION_DATA WHERE LOCATION = :location", {'location': room})

        for item in cur.fetchall():
            data = get_full_automation_data(item['ID'], db)

            if 'result' in data and data['result'] == 'nopermission':
                continue

            rules.append(data)

    return {'rules': rules}

def get_full_automation_data(id, db):
    with db:
        cur = db.cursor()

        cur.execute("SELECT * FROM AUTOMATION_DATA WHERE ID = :id", {'id': id})

        data = cur.fetchone()

        trigger_data = get_trigger_data(id, db)

        return {'name': data['NAME'], 'id': data['ID'], 'location': data['LOCATION'],
                'locationname': get_room_name(data['LOCATION'], db), 'triggerdata': trigger_data,
                'conditiondata': data['CONDITION_DATA'], 'actiondata': data['ACTION_DATA'], 'isactive': True}

def get_trigger_data(id, db):
    with db:
        cur = db.cursor()

        cur.execute("SELECT * FROM AUTOMATION_TRIGGER_DATA WHERE AUTOMATION_RULE_ID = :id", {'id': id})

        items = cur.fetchall()

        trigger_data = []

        for item in items:
            trigger_data.append({'type': item['TYPE'], 'id': item['ID'], 'value': item['VALUE'], 'text': item['TEXT']})

        return trigger_data

def add_edit_automation_rule(username, location, id, name, trigger_data, condition_data, action_data, is_active, db):
    if not has_permission(username, location, db):
        return {'result': 'nopermission'}

    add_new = (id == None or id == "" or id == "-1")

    with db:
        cur = db.cursor()

        if(add_new):
            cur.execute("INSERT INTO AUTOMATION_DATA (LOCATION, NAME, CONDITION_DATA, ACTION_DATA, IS_ACTIVE) VALUES (:location, :name, :conditions, :actions, :active)",
                        {'location': location, 'name': name, 'conditions': condition_data, 'actions': action_data, 'active': is_active})

            id = cur.lastrowid

            trigger_data = json.loads(trigger_data)

            add_trigger_data(trigger_data, id, db)
            return {'result': 'ok'}

        else:
            cur.execute("UPDATE AUTOMATION_DATA SET LOCATION = :location, NAME = :name, CONDITION_DATA = :conditions, ACTION_DATA = :actions, IS_ACTIVE = :active WHERE ID = :id",
                {'location': location, 'name': name, 'conditions': condition_data, 'actions': action_data, 'active': is_active, 'id': id})

            trigger_data = json.loads(trigger_data)

            cur.execute("DELETE FROM AUTOMATION_TRIGGER_DATA WHERE AUTOMATION_RULE_ID = :id", {'id': id})

            add_trigger_data(trigger_data, id, db)
            return {'result': 'ok'}

def delete_automation_rule(username, id, db):
    with db:
        cur = db.cursor()

        cur.execute("DELETE FROM AUTOMATION_DATA WHERE ID = :id", {'id': id})

        cur.execute("DELETE FROM AUTOMATION_TRIGGER_DATA WHERE AUTOMATION_RULE_ID = :id", {'id': id})

        return {'result': 'ok'}

def add_trigger_data(data, id, db):
    with db:
        cur = db.cursor()
        for data in data:
            param_array = {'rule': id, 'type': data['type'], 'text': data['textdata']}

            if('id' in data):
                param_array['id'] = data['id']
            else:
                param_array['id'] = None

            if('value' in data):
                param_array['value'] = data['value']
            else:
                param_array['value'] = None

            cur.execute(
                "INSERT INTO AUTOMATION_TRIGGER_DATA (AUTOMATION_RULE_ID, TYPE, ID, VALUE, TEXT) VALUES (:rule, :type, :id, :value, :text)",
                param_array)