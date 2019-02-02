#!/usr/bin/python
# -*- coding: utf-8 -*-
from homevee.VoiceAssistant.voice_patterns import PATTERN_CALCULATOR

def calculator(username, text, context, db):
    return {'msg_speech':"Taschenrechner", 'msg_text':"Taschenrechner"}

def get_pattern(db):
    return PATTERN_CALCULATOR

def get_label():
    return "calculator"

def run_command(username, text, context, db):
    return calculator(username, text, context, db)