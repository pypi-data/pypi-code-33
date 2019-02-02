#!/usr/bin/python
# -*- coding: utf-8 -*-
import random
import urllib
import urllib2
import homevee.VoiceAssistant
from homevee.VoiceAssistant import helper
from homevee.VoiceAssistant.voice_patterns import PATTERN_ACTIVITY


def get_pattern(db):
    return PATTERN_ACTIVITY

def get_label():
    return "activity"

def run_command(username, text, context, db):
    return get_activities(username, text, context, db)

def get_activities(username, text, context, db):
    try:
        url = helper.SMART_API_PATH + "/?action=activity&text=" + urllib.quote(text.encode('utf8'))
        print url

        response = urllib2.urlopen(url)
        data = response.read()

        if data is not None:
            return {'msg_speech': data, 'msg_text': data}
        else:
            output = get_error()
    except urllib2.HTTPError, e:
        output = get_error()

    return {'msg_speech': output, 'msg_text': output}

def get_error():
    return random.choice([
        'Mir fällt gerade nichts ein, was du tun könntest.'
    ])