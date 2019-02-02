#!/usr/bin/python
# -*- coding: utf-8 -*-
import random

import homevee.Functions
from homevee.VoiceAssistant.helper import generate_string

def add_to_shopping_list(username, text, context, db):
    '''words = text.split(" ")

    for i in range(0, len(words)):
        word = words[i]



    if item_count > 1:
        answer_data = [
            ['Ok']
        ]
    else:
        answer_data = [
            ['Ok']
        ]

    output = generate_string(answer_data)'''

    output = "Add Shopping List"

    return {'msg_speech': output, 'msg_text': output}

def get_shopping_list(username, text, context, db):
    items = find_items(text, db)

    if len(items) is 0:
        #Ganze Liste abfragen
        items = Functions.shopping_list.get_shopping_list(username, db)['items']

    data = [
        [['Das ', 'Folgendes '], 'steht ', 'auf ', [[['der ', 'deiner '], 'Einkaufsliste'], [['dem ', 'deinem '], 'Einkaufszettel']], ': '],
        [['Diese ', 'Folgende '], ['Artikel ', 'Produkte '], ['stehen ', 'sind '], 'auf ', [[['der ', 'deiner '], 'Einkaufsliste'],
                                                                                          [['dem ', 'deinem '], 'Einkaufszettel']], ': ']
    ]

    output = generate_string(data)

    for i in range(0, len(items)):
        item = items[i]

        if len(items) > 1:
            #Mehr als ein Element
            if i is len(items) - 1:
                # Letztes Element
                output = output + " und "
            elif i < len(items) - 1:
                # Nicht erstes und nicht letztes Element
                output = output + ", "

        output = output + str(item['amount']) + " mal " + item['item']

    return {'msg_speech': output, 'msg_text': output}

def find_items(text, db):
    items = []

    with db:
        cur = db.cursor()

        cur.execute("SELECT * FROM SHOPPING_LIST")

        for item in cur.fetchall():
            position = text.find(item['ITEM'].lower())
            if position is not -1:
                items.append({'item': item['ITEM'], 'amount': item['AMOUNT'], 'id': item['ID']})

    return items