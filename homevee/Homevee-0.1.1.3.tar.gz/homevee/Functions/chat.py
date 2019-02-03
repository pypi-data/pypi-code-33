#!/usr/bin/python
# -*- coding: utf-8 -*-
import json

import time

from homevee.firebase_utils import send_notification_to_users


def get_chat_messages(username, time, limit, db):
    messages = []

    with db:
        where_clause = ""
        params = {'limit':limit}

        if int(time) is not -1:
            where_clause = "WHERE TIMESTAMP < :time"
            params['time'] = time

        cur = db.cursor()
        cur.execute("SELECT * FROM CHAT_DATA "+where_clause+" ORDER BY TIMESTAMP DESC LIMIT :limit",
            params)

        for message in cur.fetchall():
            time_string = message['TIMESTAMP']

            #Zeit formattieren

            message_data = {'username': message['USERNAME'], 'data': json.loads(message['DATA']),
                'time': time_string, 'fromotheruser': not(username == message['USERNAME'])}
            messages.append(message_data)

        cur.close()

        return {'messages': messages}

def get_chat_image(username, imageid, db):
    return

def send_chat_message(username, data, db):

    data_array = json.loads(data)

    if data == "" or data is None or data_array is None or "msg" not in data_array:
        return {'status': 'error'}

    #if "img" in data_array:
        #Bild speichern

        #Bild in JSON-Daten einfügen

    timestamp = time.time()*1000

    with db:
        cur = db.cursor()
        cur.execute("INSERT INTO CHAT_DATA (USERNAME, DATA, TIMESTAMP) VALUES (:name, :data, :timestamp)",
            {'name': username, 'data': json.dumps(data_array), 'timestamp': timestamp})

        cur.execute("SELECT USERNAME FROM USERDATA WHERE USERNAME != :user", {'user': username})
        users = []

        for user in cur.fetchall():
            users.append(user['USERNAME'])

        send_notification_to_users(users, "Neue Nachricht von "+username, json.loads(data)['msg'], db, click_action="ChatActivity")

        cur.close()

    return {'username': username, 'data': data_array, 'time': timestamp}