#!/usr/bin/python
# -*- coding: utf-8 -*-
from homevee.VoiceAssistant.voice_patterns import PATTERN_PLACES


def get_pattern(db):
    return PATTERN_PLACES

def get_label():
    return "location"

def run_command(username, text, context, db):
    return get_places(username, text, context, db)

def get_places(username, text, context, db):
    return {'msg_speech': 'Places', 'msg_text': 'Places'}