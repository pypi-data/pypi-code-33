#!/usr/bin/python
# -*- coding: utf-8 -*-
import datetime
import re

from homevee.Functions.nutrition_data import get_nutrition_data, add_edit_user_day_nutrition_item, get_user_nutrition_overview, \
    get_user_fitness_profile
from homevee.VoiceAssistant.context_keys import ADD_NUTRITION
from homevee.VoiceAssistant.helper import set_context, generate_string
from homevee.VoiceAssistant.voice_patterns import *

MAX_PORTION_DEVIATION = 10

def get_pattern(db):
    return PATTERN_QUERY_NUTRITION_DIARY

def get_label():
    return "nutritiondiary"

def run_command(username, text, context, db):
    return voice_query_nutrition_diary(username, text, context, db)

def voice_query_nutrition_diary(username, text, context, db):
    words = text.split(" ")

    queried_value = None

    for word in words:
        if word == 'fett':
            queried_value = 'FAT'
        elif word == 'kalorien':
            queried_value = 'CALORIES'
        elif word == 'kohlenhydrate':
            queried_value = 'CARBS'
        elif word == 'zucker':
            queried_value = 'SUGAR'
        elif word in ['protein', 'proteine', 'eiweiß']:
            queried_value = 'PROTEIN'
        else:
            continue

        break

    user_profile = get_user_fitness_profile(username, db)

    print user_profile

    if (user_profile is False):
        answer = "Du hast noch kein Profil für den Ernährungsmanager erstellt. Das kannst du in der App im Menüpunkt Ernährungsmanager tun."
    elif queried_value is None:
        #Kein Wert gefunden
        answer = "Welchen Nährwert möchtest du abfragen?"

        answer_data = [
            ['Welcher Nährwert soll abgefragt werden.'],
            ['Welchen Nährwert ', ['magst', 'möchtest', 'willst'],' du abfragen.'],
        ]
    else:
        with db:
            cur = db.cursor()
            cur.execute("SELECT * FROM NUTRITION_DATA WHERE USER = :user AND DATE = :date",
                        {'user': username, 'date': datetime.datetime.today().strftime("%d.%m.%Y")})

            eaten_queried_value_today = 0

            for item in cur.fetchall():
                amount = (float(item['EATEN_PORTION_SIZE']) / float(item['PORTIONSIZE']))

                eaten_queried_value_today += item[queried_value] * amount

            unit = None

            if queried_value == 'FAT':
                value_left = user_profile['fatgoal']-eaten_queried_value_today
                unit = "Gramm Fett"
            elif queried_value == 'CALORIES':
                value_left = int(user_profile['caloriesgoal']-eaten_queried_value_today)
                eaten_queried_value_today = int(eaten_queried_value_today)
                unit = 'Kalorien'
            elif queried_value == 'CARBS':
                value_left = user_profile['carbsgoal']-eaten_queried_value_today
                unit = 'Gramm Kohlenhydrate'
            elif queried_value == 'SUGAR':
                value_left = user_profile['sugargoal']-eaten_queried_value_today
                unit = 'Gramm Zucker'
            elif queried_value == 'PROTEIN':
                value_left = user_profile['proteingoal']-eaten_queried_value_today
                unit = 'Gramm Protein'

            answer_data = [
                ['Du hast heute ', ['schon', 'bereits'], ' ', str(eaten_queried_value_today), " ", unit, ' ',
                 ['gegessen', 'verzehrt', 'aufgenommen', 'zu dir genommen'], ' und ', ['noch', 'weitere'], ' ',
                 str(value_left), ' ', unit, ' ', ['übrig', 'frei', 'offen'], '.']
            ]

            #answer = "Du hast heute schon "+str(eaten_queried_value_today)+" "+unit+" zu dir genommen und noch "+str(value_left)+" "+unit+" übrig."

    answer = generate_string(answer_data)

    return {'msg_speech': answer, 'msg_text': answer}