#!/usr/bin/python
# -*- coding: utf-8 -*-
import random

import datetime

import re

from homevee.VoiceAssistant.helper import generate_string
from homevee.VoiceAssistant.voice_patterns import PATTERN_DATE_WEEKDAY


def get_pattern(db):
    return PATTERN_DATE_WEEKDAY

def get_label():
    return "calculator"

def run_command(username, text, context, db):
    return get_weekday(username, text, context, db)

def get_weekday(username, text, context, db):
    wochentage = ['Montag', 'Dienstag', 'Mittwoch', 'Donnerstag', 'Freitag', 'Samstag', 'Sonntag']

    month_replacements = [
        ['. januar ', '.01.'],
        ['. februar ', '.02.'],
        ['. märz ', '.03.'],
        ['. april ', '.04.'],
        ['. mai ', '.05.'],
        ['. juni ', '.06.'],
        ['. juli ', '.07.'],
        ['. august ', '.08.'],
        ['. september ', '.09.'],
        ['. oktober ', '.10.'],
        ['. november ', '.11.'],
        ['. dezember ', '.12.'],
    ]

    for replacement in month_replacements:
        text = text.replace(replacement[0], replacement[1])

    date = re.search('\d{2}\.\d{2}\.\d{4}', text)
    if(date is None):
        answer_data = [
            ['Du hast kein Datum ', ['gesagt', 'genannt'],'.'],
            ['Du musst', [' mir ', ' '], ['zuerst', 'erst', 'erst einmal'], ' ein Datum ', ['nennen', 'sagen'], '.']
        ]

        output = generate_string(answer_data)
    else:
        date_formatted = str(datetime.datetime.strptime(date.group(), '%d.%m.%Y').date())

        print(date_formatted)

        date_data = date_formatted.split('-')
        time = datetime.datetime(int(date_data[0]), int(date_data[1]), int(date_data[2]))
        wochentag = wochentage[time.weekday()]

        print(time.weekday())

        answer_data = [
            [[['Der ', date_formatted], 'Das'], ' ist ein ', wochentag, [', '+username, ''], '.']
        ]

        output = generate_string(answer_data)

    return {'msg_speech': output, 'msg_text': output}