#!/usr/bin/python
# -*- coding: utf-8 -*-
import json

from homevee.Functions.condition_actions.actions import run_actions


def get_voice_commands(db):

    rules = []

    with db:
        cur = db.cursor()

        cur.execute("SELECT * FROM CUSTOM_VOICE_COMMANDS")

        for item in cur.fetchall():
            commands = get_command_data(item['ID'], db)
            responses = get_response_data(item['ID'], db)

            rules.append({'id': item['ID'], 'name': item['NAME'], 'action_data': item['ACTION_DATA'],
                          'command_data': commands, 'response_data': responses})

    return {'rules': rules}

def get_command_data(id, db):
    with db:
        cur = db.cursor()

        cur.execute("SELECT * FROM CUSTOM_VOICE_COMMAND_SENTENCES WHERE COMMAND_ID = :id", {'id': id})

        items = cur.fetchall()

        data = []

        for item in items:
            data.append(item['COMMAND'])

        return data

def get_response_data(id, db):
    with db:
        cur = db.cursor()

        cur.execute("SELECT * FROM CUSTOM_VOICE_COMMAND_RESPONSES WHERE COMMAND_ID = :id", {'id': id})

        items = cur.fetchall()

        data = []

        for item in items:
            data.append(item['RESPONSE'])

        return data

def add_edit_voice_command(username, id, name, command_data, response_data, action_data, db):
    add_new = (id == None or id == "" or id == "-1")

    with db:
        cur = db.cursor()

        if(add_new):
            cur.execute("INSERT INTO CUSTOM_VOICE_COMMANDS (NAME, ACTION_DATA) VALUES (:name, :actions)",
                        {'name': name, 'actions': action_data})

            id = cur.lastrowid

            command_data = json.loads(command_data)
            add_command_data(command_data, id, db)

            response_data = json.loads(response_data)
            add_response_data(response_data, id, db)
            return {'result': 'ok'}

        else:
            cur.execute("UPDATE AUTOMATION_DATA SET NAME = :name, ACTION_DATA = :actions WHERE ID = :id",
                {'name': name, 'actions': action_data, 'id': id})

            cur.execute("DELETE FROM CUSTOM_VOICE_COMMAND_SENTENCES WHERE COMMAND_ID = :id", {'id': id})
            cur.execute("DELETE FROM CUSTOM_VOICE_COMMAND_RESPONSES WHERE COMMAND_ID = :id", {'id': id})


            command_data = json.loads(command_data)
            add_command_data(command_data, id, db)

            response_data = json.loads(response_data)
            add_response_data(response_data, id, db)

            return {'result': 'ok'}

def delete_voice_command(username, id, db):
    with db:
        cur = db.cursor()

        cur.execute("DELETE FROM CUSTOM_VOICE_COMMANDS WHERE ID = :id", {'id': id})

        cur.execute("DELETE FROM CUSTOM_VOICE_COMMAND_RESPONSES WHERE COMMAND_ID = :id", {'id': id})

        cur.execute("DELETE FROM CUSTOM_VOICE_COMMAND_SENTENCES WHERE COMMAND_ID = :id", {'id': id})

        return {'result': 'ok'}

def add_command_data(commands, id, db):
    with db:
        cur = db.cursor()
        for command in commands:
            param_array = {'id': id, 'command': command.lower()}

            cur.execute(
                "INSERT INTO CUSTOM_VOICE_COMMAND_SENTENCES (COMMAND_ID, COMMAND) VALUES (:id, :command)",
                param_array)

def add_response_data(responses, id, db):
    with db:
        cur = db.cursor()
        for response in responses:
            param_array = {'id': id, 'response': response}

            cur.execute(
                "INSERT INTO CUSTOM_VOICE_COMMAND_RESPONSES (COMMAND_ID, RESPONSE) VALUES (:id, :response)",
                param_array)

def run_custom_voice_commands(text, username, db):
    with db:
        cur = db.cursor()

        cur.execute("SELECT * FROM CUSTOM_VOICE_COMMAND_SENTENCES, CUSTOM_VOICE_COMMANDS WHERE ID = COMMAND_ID AND COMMAND = :command",
                    {'command': text})

        result = cur.fetchone()

        if(result is None):
            return None

        id = result['ID']

        action_data = result['ACTION_DATA']

        action_data = json.loads(action_data)

        #run actions
        run_actions(action_data, db)

        cur.execute("SELECT * FROM CUSTOM_VOICE_COMMAND_RESPONSES WHERE COMMAND_ID = :id ORDER BY RANDOM()",
                    {'id': id})

        return cur.fetchone()['RESPONSE']