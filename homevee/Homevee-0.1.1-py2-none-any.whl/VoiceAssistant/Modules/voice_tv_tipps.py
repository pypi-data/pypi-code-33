#!/usr/bin/python
# -*- coding: utf-8 -*-

from homevee.Functions.tv_data import get_tv_plan
from homevee.VoiceAssistant import helper
from homevee.VoiceAssistant.voice_patterns import PATTERN_TV_TIPPS

def get_pattern(db):
    return PATTERN_TV_TIPPS

def get_label():
    return "tvprogrammtipps"

def run_command(username, text, context, db):
    return get_tv_tipps(username, text, context, db)

def get_tv_tipps(username, text, context, db):
    tv_shows = get_tv_plan(username, "tipps", db)

    VERB = ['kommt', 'läuft']

    show_strings = []
    for show in tv_shows:
        TIME = show['time'] + ' Uhr'
        CHANNEL = show['channel']
        NAME = '\''+show['name']+'\''

        string_data = [
            ['um ', TIME, ' ', VERB, ' auf ', CHANNEL,  ' ', NAME],
            ['um ', TIME, ' ', VERB, ' ', NAME, ' auf ', CHANNEL],
            ['auf ', CHANNEL, ' um ', TIME, ' ', VERB, ' ', NAME],
            ['auf ', CHANNEL, ' ', VERB, ' ', NAME, ' um ', TIME],
            [NAME, ' ', VERB, ' um ', TIME, ' auf ', CHANNEL],
            [NAME, ' ', VERB, ' auf ', CHANNEL, ' um ', TIME],
        ]

        show_strings.append(helper.generate_string(string_data))

    show_string = None
    for i in range(0, len(show_strings)):
        if show_string is None:
            show_string = show_strings[i]
        elif i == len(show_strings)-1:
            if i != 0:
                show_string = show_string + ' und '
            show_string = show_string+show_strings[i]
        else:
            show_string = show_string+', '+show_strings[i]

    answer_data = [
        [['Die', 'Deine'], ' ', ['TV', 'Fernseh', 'Programm'], '-', ['Tipps', 'Vorschläge', 'Empfehlungen'], ' ',
            ['heute', 'für heute'], ' ', ['sind', 'lauten'], ':']
    ]

    output = helper.generate_string(answer_data) + ' ' + show_string + '.'

    return {'msg_speech': output, 'msg_text': output}