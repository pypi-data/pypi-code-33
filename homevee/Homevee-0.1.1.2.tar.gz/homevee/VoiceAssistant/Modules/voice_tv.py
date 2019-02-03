#!/usr/bin/python
# -*- coding: utf-8 -*-

from homevee.Functions.tv_data import get_tv_plan
from homevee.VoiceAssistant import helper
from homevee.VoiceAssistant.voice_patterns import PATTERN_TV

def get_pattern(db):
    return PATTERN_TV

def get_label():
    return "tvprogramm"

def run_command(username, text, context, db):
    return get_tv(username, text, context, db)

def get_tv(username, text, context, db):
    return {'msg_speech':'TV-Programm', 'msg_text':'TV-Programm'}