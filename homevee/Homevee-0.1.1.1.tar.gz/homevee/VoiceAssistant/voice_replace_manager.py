#!/usr/bin/python
# -*- coding: utf-8 -*-
import json

from homevee.Helper.helper_functions import has_permission


def get_voice_replace_items(username, db):
    if not has_permission(username, "admin", db):
        return {'status': 'noadmin'}

    replace = []

    with db:
        cur = db.cursor()
        cur.execute("SELECT DISTINCT REPLACE_WITH FROM VOICE_COMMAND_REPLACE WHERE USERNAME = :user",
                    {'user': username})

        for item in cur.fetchall():
            cur.execute("SELECT TEXT FROM VOICE_COMMAND_REPLACE WHERE REPLACE_WITH == :item AND USERNAME = :user",
                {'user': username, 'item': item['REPLACE_WITH']})

            replacements = []

            for replacement in cur.fetchall():
                replacements.append(replacement['TEXT'])

            replace.append({'replacewith': item['REPLACE_WITH'], 'replacearray': replacements})

        cur.close()

        return {'replacedata': replace}

def add_edit_voice_replace_item(username, replacewith, replaceitems, db):
    with db:
        cur = db.cursor()

        replaceitems = json.loads(replaceitems)

        cur.execute("DELETE FROM VOICE_COMMAND_REPLACE WHERE REPLACE_WITH = :replacewith AND USERNAME = :user",
                    {'replacewith': replacewith, 'user': username})

        for item in replaceitems:
            cur.execute("INSERT INTO VOICE_COMMAND_REPLACE (USERNAME, REPLACE_WITH, TEXT) VALUES (:user, :replacewith, :text)",
                        {'user': username, 'replacewith': replacewith, 'text': item})

    return {'result': 'ok'}

def delete_voice_replace_item(username, replacewith, db):
    with db:
        cur = db.cursor()

        cur.execute("DELETE FROM VOICE_COMMAND_REPLACE WHERE REPLACE_WITH = :replacewith AND USERNAME = :user",
                    {'replacewith': replacewith, 'user': username})

    return {'result': 'ok'}