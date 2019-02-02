#!/usr/bin/python
# -*- coding: utf-8 -*-
from homevee.colors import COLORS
from homevee.device_types import *

PATTERN_SET_MODES = [
    [['mach', 'schalt'], ['an','ein','aus']]
]

PATTERN_SET_THERMOSTAT = [
    [['mach', 'stell', 'dreh'], ['thermostat', 'temperatur', 'heizung', 'heizkörper'],['aus','auf']]
]

PATTERN_CONTROL_BLINDS = [
    [['mach', 'stell', 'fahr'], ['jalousie', 'jalousien', 'rollladen', 'rollläden', 'rolladen', 'rolläden', 'rollo'],
     ['rauf', 'runter', 'herunter', ['nach', 'oben'], ['nach', 'unten'], 'hoch', 'zu','auf']]
]

PATTERN_SET_DIMMER = [
    [['mach', 'stell', 'dreh'],['aus','auf'],'prozent']
]

PATTERN_CALCULATOR = [
    ['wie', 'viel',['ist','ergibt']],
    ['was',['ist','ergibt']]
]

PATTERN_JOKE = [
    [['erzähl','sag'],'witz'],
    ['klopf', 'klopf']
]

PATTERN_WEATHER = [
    ['wie',['ist','wird'],'wetter'],
    ['regnet','es'],
    ['gibt','regen'],
    ['wird','regnen']
]

PATTERN_TV = [
    ['was',['kommt','ist','gibt','läuft'],['tv','fernsehen','fernseher']]
]

PATTERN_TV_TIPPS = [
    [['was', 'welche'], 'sind', ['tv-tipps', 'tvtipps', 'tv-tips', 'tvtips']],
    [['was', 'welche'], 'sind', ['tv', 'fernseh'], ['tipps', 'tips']],
    [['was', 'welche'], 'sind', ['fernseh-tipps', 'fernsehtipps', 'fernseh-tips', 'fernsehtips']],
]

PATTERN_GET_CALENDAR = [
    ['was', 'steht', 'an'],
    ['was', 'habe', 'ich', 'vor'],
    ['habe', 'ich', 'termine']
]

PATTERN_ADD_CALENDAR = [
    ['erinnere', 'mich']
]

PATTERN_GET_SHOPPING_LIST = [
    ['was', ['steht', 'ist'], ['einkaufszettel', 'einkaufsliste']],
    ['was', ['muss', 'soll'], 'kaufen'],
    ['wie', ['viel', 'viele'], ['muss', 'soll'], 'kaufen']
]

PATTERN_ADD_SHOPPING_LIST = [
    [['schreibe', 'setze'], ['auf', 'zur', 'in'], ['einkaufsliste','einkaufliste','einkaufszettel']]
]

PATTERN_PLACES = [
    [['wo', 'was'], 'ist', ['der', 'die', 'das'], ['nähste', 'nächste']]
]

PATTERN_SUMMARY = [
    ['was', 'so', 'los'],
    ['was', 'gibt']
]

PATTERN_RECIPES = [
    ['zeig', 'mir', 'rezepte', ['über', 'für', 'zu', 'von']]
]

PATTERN_WIKIPEDIA = [
    [['wer', 'was'], ['ist', 'war']]
]

PATTERN_MOVIE_RATING = [
    ['wie', 'ist', 'film'],
    ['wie', ['gut', 'schlecht'], 'ist', 'film'],
    ['ist', 'film', ['gut', 'schlecht']]
]

PATTERN_DATE_WEEKDAY = [
    ['was', 'ist', 'für', ['tag', 'wochentag']]
]

PATTERN_ROUTE = [
    ['wie', 'weit', 'ist', ['bis', 'zu', 'nach']],
    ['wie', ['lang', 'lange'], ['braucht', 'brauche'], ['bis', 'zu', 'nach']]
]

SENSOR_ADJECTIVES = ['warm', 'kalt', 'dunkel', 'hell', 'feucht', 'laut']
SENSOR_SUBJECTIVES = ['temperatur', 'helligkeit', 'luftfeuchtigkeit', 'lautstärke', 'verbrauch', 'stromverbrauch']
PATTERN_SENSOR_DATA = [
    ['wie', SENSOR_ADJECTIVES, 'ist'],
    ['wie', 'ist', ['der', 'die', 'das'], SENSOR_SUBJECTIVES]
]

PATTERN_REED_SENSOR_DATA = [
    [['ist', 'sind'], ['tür', 'türen', 'fenster'], ['geschlossen', 'zu', 'geöffnet', 'offen', 'auf']]
]

PATTERN_PRESENCE_SENSOR_DATA = [
    ['ist', 'jemand', ['in', 'im']]
]

PATTERN_ACTIVITY = [
    [['mir', 'uns'], 'ist', 'langweilig'],
    ['was', ['kann', 'können'], ['ich', 'wir'], ['tun', 'machen', 'unternehmen']]
]

PATTERN_WOL = [
    ['fahr', 'hoch']
]

PATTERN_RGB_CONTROL = [
    [['mach', 'stell', 'tu', 'dreh'], COLORS]
]

PATTERN_ADD_NUTRITION_ITEM = [
    ['ich', ['gegessen', 'essen', 'esse', 'getrunken', 'trinke', 'trink']]
]

PATTERN_NUTRITION_INFO = [
    ['wie', ['viel', 'viele'], ['fett', 'kalorien', 'kohlenhydrate', 'eiweiß', 'protein', 'zucker'], ['hat', 'ist', 'haben', 'sind']]
]

PATTERN_QUERY_NUTRITION_DIARY = [
    ['wie', ['viel', 'viele'], ['fett', 'kalorien', 'kohlenhydrate', 'eiweiß', 'protein', 'zucker'], ['ist', 'sind', 'habe'], ['übrig', 'offen', 'auf', 'erlaubt']],
    ['wie', ['viel', 'viele'], ['fett', 'kalorien', 'kohlenhydrate', 'eiweiß', 'protein', 'zucker'], ['darf', 'kann', 'soll', 'muss'], ['essen', 'trinken', 'verzehren', ['zu', 'mir', 'nehmen']]]
]

def GET_PATTERN_SET_MODES(db):
    with db:
        cur = db.cursor()
        data = [
            ['FUNKSTECKDOSEN','NAME','DEVICE',FUNKSTECKDOSE],
            ['ZWAVE_SWITCHES','NAME','ID',ZWAVE_SWITCH],
            ['URL_SWITCH_BINARY','NAME','ID',URL_SWITCH],
            ['URL_TOGGLE','NAME','ID',URL_TOGGLE],
            ['PHILIPS_HUE_LIGHTS','NAME','ID',PHILIPS_HUE_LIGHT],
            ['URL_RGB_LIGHT','NAME','ID',URL_RGB_LIGHT]
        ]
        device_names = []
        for item in data:
            cur.execute("SELECT * FROM "+item[0])
            for device in cur.fetchall():
                device_names.append(device[item[1]].lower())
    output_array = [
        [['mach', 'schalt'], device_names, ['an','ein','aus']],
        [device_names, ['an','ein','aus']]
    ]
    #print output_array
    return output_array

def GET_PATTERN_WOL(db):
    with db:
        cur = db.cursor()
        data = [
            ['WAKE_ON_LAN','NAME','DEVICE',WAKE_ON_LAN],
            ['XBOX_ONE_WOL','NAME','ID',XBOX_ONE_WOL]
        ]
        device_names = []
        for item in data:
            cur.execute("SELECT * FROM "+item[0])
            for device in cur.fetchall():
                device_names.append(device[item[1]].lower())
    output_array = [
        [['fahr'], device_names, ['hoch']]
    ]
    return output_array
