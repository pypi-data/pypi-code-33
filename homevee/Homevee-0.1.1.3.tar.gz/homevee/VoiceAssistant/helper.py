#!/usr/bin/python
# -*- coding: utf-8 -*-
import json
import random

import time
import urllib2
import codecs
import json
import random
import urllib
import urllib2

CONTEXT_VALIDITY = 60

SMART_API_PATH = "https://api.homevee.de/api.php"

def contains_pattern(patterns, text):
    for pattern in patterns:
        #print pattern
        if is_in_order(pattern, text):
            return True
    return False

def is_in_order(words, text):
    indices = []

    word_parts = text.split(" ")

    for word in words:
        found = False
        if isinstance(word, list):
            for word_item in word:
                if found:
                    break
                #print word_item

                if(word_item in word_parts):
                    if(len(indices) > 0):
                        max_index = indices[len(indices)-1]
                        indices.append(word_parts.index(word_item, max_index+1))
                    else:
                        indices.append(word_parts.index(word_item))
                    #print word_item+" found"
                    found = True

            if not found:
                return False
        else:
            #print word

            if (word in word_parts):
                if(len(indices) > 0):
                    max_index = indices[len(indices)-1]
                    indices.append(word_parts.index(word, max_index+1))
                else:
                    indices.append(word_parts.index(word))
                #print word+" found"
            else:
                return False

    last_value = -1
    for index in indices:
        if index is -1 or index <= last_value:
            return False
        last_value = index
    return True

def is_in_order_backup(words, text):
    indices = []

    for word in words:
        found = False
        if isinstance(word, list):
            for word_item in word:
                if found:
                    break
                #print word_item
                position = text.find(word_item)
                if position is not -1:
                    indices.append(position)
                    found = True
            if not found:
                return False
        else:
            #print word
            position = text.find(word)
            if position is not -1:
                indices.append(position)
            else:
                return False

    last_value = -1
    for index in indices:
        if index is -1 or index <= last_value:
            return False
        last_value = index
    return True

def get_no_permission_text():
    return random.choice(["Du hast nicht die nötigen Berechtigungen für diese Aktion.",
		"Dazu fehlen dir die Berechtigungen.",
		"Das darfst du nicht."])

def classify_voice_command(request):
    url = "https://assistant.homevee.de:444/"
    data = urllib2.urlopen(url + urllib.quote(codecs.encode(request, 'utf-8'))).read()
    return json.loads(data)

def generate_string(answer_data):
    if not isinstance(answer_data, list):
        return str(answer_data)

    chosen_answer = random.choice(answer_data)

    output = ""

    if isinstance(chosen_answer, list):
        for part in chosen_answer:
            output = output + generate_string(part)
    else:
        return str(chosen_answer)
    return str(output)

def set_context(username, context_key, context_data, db):

    print context_data

    context_data = json.dumps(context_data)

    with db:
        cur = db.cursor()

        cur.execute("DELETE FROM 'VOICE_COMMAND_USER' WHERE USERNAME == :user",
                    {'user': username})

        cur.execute("INSERT INTO VOICE_COMMAND_USER (USERNAME, CONTEXT_TIME, CONTEXT_KEY, CONTEXT_DATA) VALUES (:username, :time, :key, :data)",
                    {'username': username, 'time': int(time.time()), 'key': context_key, 'data': context_data})

def get_context(username, db):
    with db:
        cur = db.cursor()
        cur.execute("SELECT * FROM 'VOICE_COMMAND_USER' WHERE USERNAME == :user",
                    {'user': username})

        data = cur.fetchone()

        if data:
            context_data = data

            if(int(time.time()) - int(context_data['CONTEXT_TIME'])) <= CONTEXT_VALIDITY:
                cur.execute("DELETE FROM 'VOICE_COMMAND_USER' WHERE USERNAME == :user",
                            {'user': username})

                return context_data
            return None
        else:
            return None

def find_room(text, db):
    with db:
        cur = db.cursor()

        cur.execute("SELECT * FROM ROOMS")

        for room in cur.fetchall():
            position = text.find(room['NAME'].lower());
            if position is not -1:
                return room
    return None

def is_number(s):
    try:
        float(s)
        return True
    except ValueError:
        return False

def get_okay():
    try:
        url = SMART_API_PATH + "/?action=okay"
        print url

        response = urllib2.urlopen(url)
        data = response.read()

        if data is not None:
            return data
    except urllib2.HTTPError, e:
        print e
        return ['Sehr gern', 'Ok', 'Alles klar']

def replace_voice_commands(text, username, db):
    with db:
        cur = db.cursor()

        cur.execute("SELECT * FROM VOICE_COMMAND_REPLACE WHERE USERNAME = :user",
                    {'user': username})

        for item in cur.fetchall():
            text = text.replace(item['TEXT'], item['REPLACE_WITH'])

        return text

def user_is_at_home(username, db):
    with db:
        cur = db.cursor()
        cur.execute("SELECT * FROM USERDATA WHERE USERNAME = :username", {'username': username})

        user = cur.fetchone()

        return user['AT_HOME']