#!/usr/bin/python
# -*- coding: utf-8 -*-
import json
import urllib
import xml.etree.ElementTree as etree

def get_tv_plan(username, type, db):
    tv_channels = get_tv_channels(username, db)

    if type == "2015":
        type = "heute2015"
    elif type == "2200":
        type = "heute2200"
    elif type == "jetzt":
        type = "jetzt"
    elif type == "tipps":
        type = "tipps"
    else:
        raise AttributeError("TV-Typ '" + type + "' nicht vorhanden")

    tv_shows = []

    link = "http://www.tvspielfilm.de/tv-programm/rss/" + type + ".xml"

    file = urllib.urlopen(link)
    data = file.read()
    file.close()

    #XML-Datei laden
    ergebnis = etree.fromstring(data)

    for item in ergebnis.find('channel').findall('item'):
        zeit, channel, name = item.find('title').text.split(" | ")

        description = item.find('description').text

        img = None
        if item.find('image') is not None:
            img = item.find('enclosure').attrib['url']

        if type == "tipps" or ((tv_channels is None) or (channel in tv_channels)):
            tv_shows.append({'time': zeit, 'channel': channel, 'name': name, 'description': description, 'img': img})

    return tv_shows

def get_tv_channels(username, db):
    cur = db.cursor()
    cur.execute("SELECT * FROM TV_CHANNELS WHERE USERNAME == :username", {'username': username})

    channels = []

    for channel in cur.fetchall():
        channels.append(channel['CHANNEL'])

    return channels

def get_all_tv_channels(username, db):
    selected_channels = get_tv_channels(username, db)

    #XML-Datei von Link laden
    link = "http://www.tvspielfilm.de/tv-programm/rss/jetzt.xml"

    file = urllib.urlopen(link)
    data = file.read()
    file.close()

    # XML-Datei laden
    ergebnis = etree.fromstring(data)

    channels = []
    for item in ergebnis.find('channel').findall('item'):
        zeit, channel, name = item.find('title').text.split(" | ")

        if (channels is None) or (channel not in channels):
            channels.append({'name': channel, 'selected': (channel in selected_channels)})

    return channels

def set_tv_channels(username, json_data, db):
    cur = db.cursor()
    cur.execute("DELETE FROM TV_CHANNELS WHERE USERNAME == :username", {'username': username})

    #Abfrage erfolgreich?
    if False:
        return {'status': 'error'}
    else:
        channels = json.loads(json_data)

        for channel in channels:
            cur.execute("INSERT INTO TV_CHANNELS (USERNAME, CHANNEL) VALUES (?,?)",
                [username, channel])

        return {'status': 'ok'}