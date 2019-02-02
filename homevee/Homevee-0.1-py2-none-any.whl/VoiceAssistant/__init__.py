#!/usr/bin/python
# -*- coding: utf-8 -*-
import codecs
import json
import random

import time
import urllib

from homevee.Manager.custom_voice_commands import run_custom_voice_commands
from context_keys import *
from homevee.VoiceAssistant import voice_patterns, Modules, helper
import sys

reload(sys)
sys.setdefaultencoding('utf8')

def voice_command_cloud(username, text, user_last_location, room, db):
    # return {'msg_speech': "Der Assistent ist noch nicht erreichbar.", 'msg_text': "Der Assistent ist zur Zeit noch nicht fertig, wird aber gerade implementiert."}

    # room => damit z.b. bei "mach das licht an" das licht im richtigen raum angeht

    # print "voice_command"

    text = text.lower()

    text = helper.replace_voice_commands(text, username, db)

    # run custom voice_commands
    answer = run_custom_voice_commands(text, username, db)

    if (answer is not None):
        return {'msg_speech': answer, 'msg_text': answer}

    print "Voice command: " + codecs.encode(text, 'utf-8')

    context = helper.get_context(username, db)

    if context is not None:
        context_data = json.loads(context['CONTEXT_DATA'])

        print "Kontext: " + str(context_data)

        if context['CONTEXT_KEY'] == SET_MODES:
            answer = Modules.voice_set_modes.set_modes_voice(username, text, context_data, db)
        elif context['CONTEXT_KEY'] == SET_THERMOSTAT:
            answer = Modules.voice_set_modes.set_thermostat(username, text, context_data, db)
        elif context['CONTEXT_KEY'] == CONTROL_BLINDS:
            answer = Modules.voice_set_modes.control_blinds(username, text, context_data, db)
        elif context['CONTEXT_KEY'] == GET_WEATHER:
            answer = Modules.voice_weather.get_weather(username, text, context_data, db)
        elif context['CONTEXT_KEY'] == ADD_NUTRITION:
            answer = Modules.voice_nutrition_manager.voice_add_nutrition_item(username, text, context_data, db)
        elif context['CONTEXT_KEY'] == TV_PROGRAMME:
            answer = Modules.voice_tv.get_tv(username, text, context_data, db)
        elif context['CONTEXT_KEY'] == GET_SENSOR_DATA:
            answer = Modules.voice_get_sensor_data.get_sensor_data(username, text, context_data, db)

        if answer is None or not answer:
            return voice_command_cloud(username, text, user_last_location, room, db)

    else:
        MIN_CONFIDENCE = 0.95

        try:
            result = helper.classify_voice_command(text)
        except:
            return voice_command(username, text, user_last_location, room, db)

        print result

        label = result['label']
        confidence = result['confidence']

        voice_modules = [Modules.voice_calculator, Modules.voice_set_modes, Modules.voice_calendar,
                         Modules.voice_conversation, Modules.voice_get_sensor_data, Modules.voice_tv,
                         Modules.voice_jokes, Modules.voice_rgb_control, Modules.voice_weather,
                         Modules.voice_tv_tipps, Modules.voice_movie_api]

        module_map = {}

        for module in voice_modules:
            module_map[module.get_label()] = module.run_command

        if confidence >= MIN_CONFIDENCE and label in module_map:
            answer = module_map[label](username, text, context, db)
        else:
            answer = Modules.voice_conversation.conversation(username, text, context, db)

    return (answer)

def voice_command(username, text, user_last_location, room, db):
    #return {'msg_speech': "Der Assistent ist noch nicht erreichbar.", 'msg_text': "Der Assistent ist zur Zeit noch nicht fertig, wird aber gerade implementiert."}

    #room => damit z.b. bei "mach das licht an" das licht im richtigen raum angeht

    #print "voice_command"

    text = text.lower()

    try:
        helper.classify_voice_command(text)
    except:
        print "homevee assistant not working"

    text = helper.replace_voice_commands(text, username, db)

    #run custom voice_commands
    answer = run_custom_voice_commands(text, username, db)

    if(answer is not None):
        return {'msg_speech': answer, 'msg_text': answer}

    print "Voice command: "+codecs.encode(text, 'utf-8')

    context = helper.get_context(username, db)

    if context is not None:
        context_data = json.loads(context['CONTEXT_DATA'])

        print "Kontext: "+str(context_data)

        if context['CONTEXT_KEY'] == SET_MODES:
            answer = Modules.voice_set_modes.set_modes_voice(username, text, context_data, db)
        elif context['CONTEXT_KEY'] == SET_THERMOSTAT:
            answer = Modules.voice_set_modes.set_thermostat(username, text, context_data, db)
        elif context['CONTEXT_KEY'] == CONTROL_BLINDS:
            answer = Modules.voice_set_modes.control_blinds(username, text, context_data, db)
        elif context['CONTEXT_KEY'] == GET_WEATHER:
            answer = Modules.voice_weather.get_weather(username, text, context_data, db)
        elif context['CONTEXT_KEY'] == ADD_NUTRITION:
            answer = Modules.voice_nutrition_manager.voice_add_nutrition_item(username, text, context_data, db)
        elif context['CONTEXT_KEY'] == TV_PROGRAMME:
            answer = Modules.voice_tv.get_tv(username, text, context_data, db)
        elif context['CONTEXT_KEY'] == GET_SENSOR_DATA:
            answer = Modules.voice_get_sensor_data.get_sensor_data(username, text, context_data, db)

        if answer is None or not answer:
            return voice_command(username, text, user_last_location, room, db)

    else:
        #Schalter
        if helper.contains_pattern(voice_patterns.GET_PATTERN_SET_MODES(db), text):
            answer = Modules.voice_set_modes.run_command(username, text, context, db)
        #if contains_pattern(voice_patterns.PATTERN_SET_MODES, text):
        #    answer = set_modes_voice(username, text, context, db)
        #Schalter
        elif helper.contains_pattern(voice_patterns.GET_PATTERN_WOL(db), text):
            answer = Modules.voice_wol.voice_wol(username, text, context, db)
        #Thermostat
        elif helper.contains_pattern(voice_patterns.PATTERN_SET_THERMOSTAT, text):
            answer = Modules.voice_set_modes.set_thermostat(username, text, context, db)
        #Rolladensteuerung
        elif helper.contains_pattern(voice_patterns.PATTERN_CONTROL_BLINDS, text):
            answer = Modules.voice_set_modes.control_blinds(username, text, context, db)
        #Dimmer
        elif helper.contains_pattern(voice_patterns.PATTERN_SET_DIMMER, text):
            answer = Modules.voice_set_modes.set_dimmer(username, text, context, db)
        #Einkaufsliste
        elif helper.contains_pattern(voice_patterns.PATTERN_ADD_SHOPPING_LIST, text):
            answer = Modules.voice_shopping_list.add_to_shopping_list(username, text, context, db)
        elif helper.contains_pattern(voice_patterns.PATTERN_GET_SHOPPING_LIST, text):
            answer = Modules.voice_shopping_list.get_shopping_list(username, text, context, db)
        #Wochentag
        elif helper.contains_pattern(voice_patterns.PATTERN_DATE_WEEKDAY, text):
            answer = Modules.voice_get_weekday.run_command(username, text, context, db)
        #Wetter
        elif helper.contains_pattern(voice_patterns.PATTERN_WEATHER, text):
            answer = Modules.voice_weather.run_command(username, text, context, db)
        #TV-Programm
        elif helper.contains_pattern(voice_patterns.PATTERN_TV, text):
            answer = Modules.voice_tv.run_command(username, text, context, db)
        elif helper.contains_pattern(voice_patterns.PATTERN_TV_TIPPS, text):
            answer = Modules.voice_tv_tipps.run_command(username, text, context, db)
        #Witz
        #elif contains_pattern(voice_patterns.PATTERN_JOKE, text):
        #    answer = get_joke(username, text, context, db)
        #Kalender
        elif helper.contains_pattern(voice_patterns.PATTERN_ADD_CALENDAR, text):
            answer = Modules.voice_add_calendar.run_command(username, text, context, db)
        elif helper.contains_pattern(voice_patterns.PATTERN_GET_CALENDAR, text):
            answer = Modules.voice_calendar.run_command(username, text, context, db)
        #Places
        elif helper.contains_pattern(voice_patterns.PATTERN_PLACES, text):
            answer = Modules.voice_places_api.get_places(username, text, context, db)
        #Summary
        elif helper.contains_pattern(voice_patterns.PATTERN_SUMMARY, text):
            answer = Modules.voice_summary.get_voice_summary(username, text, context, db)
        #Rezepte
        elif helper.contains_pattern(voice_patterns.PATTERN_RECIPES, text):
            answer = Modules.voice_recipes.run_command(username, text, context, db)
        #Wikipedia
        elif helper.contains_pattern(voice_patterns.PATTERN_WIKIPEDIA, text):
            answer = Modules.voice_wikipedia.run_command(username, text, context, db)
        #Movie Rating
        elif helper.contains_pattern(voice_patterns.PATTERN_MOVIE_RATING, text):
            answer = Modules.voice_movie_api.run_command(username, text, context, db)
        #Routendaten
        elif helper.contains_pattern(voice_patterns.PATTERN_ROUTE, text):
            answer = Modules.voice_route.get_distance_data(username, text, context, db)
        #Aktivitäten abfragen
        #elif contains_pattern(voice_patterns.PATTERN_ACTIVITY, text):
        #    answer = get_activities(username, text, context, db)
        #Sensordaten abfragen
        elif helper.contains_pattern(voice_patterns.PATTERN_SENSOR_DATA, text):
            answer = Modules.voice_get_sensor_data.run_command(username, text, context, db)
        elif helper.contains_pattern(voice_patterns.PATTERN_REED_SENSOR_DATA, text):
            answer = Modules.voice_get_sensor_data.get_reed_data(username, text, context, db)
        elif helper.contains_pattern(voice_patterns.PATTERN_PRESENCE_SENSOR_DATA, text):
            answer = Modules.voice_get_sensor_data.get_presence_data(username, text, context, db)
        #RGB Lichter steuern
        elif helper.contains_pattern(voice_patterns.PATTERN_RGB_CONTROL, text):
            answer = Modules.voice_rgb_control.run_command(username, text, context, db)
        #Nährwertmanager
        elif helper.contains_pattern(voice_patterns.PATTERN_QUERY_NUTRITION_DIARY, text):
            answer = Modules.voice_nutrition_diary.run_command(username, text, context, db)
        elif helper.contains_pattern(voice_patterns.PATTERN_NUTRITION_INFO, text):
            answer = Modules.voice_nutrition_manager.run_command(username, text, context, db)
        elif helper.contains_pattern(voice_patterns.PATTERN_ADD_NUTRITION_ITEM, text):
            answer = Modules.voice_add_nutrition_data.run_command(username, text, context, db)
        # Taschenrechner
        elif helper.contains_pattern(voice_patterns.PATTERN_CALCULATOR, text):
            answer = Modules.voice_calculator.calculator(username, text, context, db)
        #Unterhaltung
        else:
            answer = Modules.voice_conversation.conversation(username, text, context, db)

    return(answer)
