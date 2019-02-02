#!/usr/bin/python
# -*- coding: utf-8 -*-
import json
import urllib2

import re

from homevee.VoiceAssistant.helper import generate_string, is_number
from homevee.VoiceAssistant.voice_patterns import PATTERN_WIKIPEDIA

MIN_OUTPUT_LENGTH = 100

def get_pattern(db):
    return PATTERN_WIKIPEDIA

def get_label():
    return "wikipedia"

def run_command(username, text, context, db):
    return voice_definition(username, text, context, db)

def voice_definition(username, text, context, db):
    words = text.split(" ")

    definition = []

    query = None

    is_query = False

    for word in words:
        if is_query:
            if query is None:
                query = word.capitalize()
            else:
                query = query + " " + word.capitalize()

        if word == "ist" or word == "war":
            is_query = True

    url = 'https://de.wikipedia.org/w/api.php?format=json&action=query&prop=extracts&exintro=&explaintext=&titles='+query.replace(" ", "%20")
    response = urllib2.urlopen(url).read()

    print(url)

    print(response)

    data = json.loads(response)

    pages = data['query']['pages']

    page_keys = list(pages.keys())[0]

    if 'extract' in pages[page_keys]:
        definition = pages[page_keys]['extract']

    if  page_keys == -1 or len(definition) == 0:
        answers = [
            ['Ich habe ', ['zu ', 'über '], ' ', query, ' ' , ['leider ', 'bedauerlicherweise ', ''], [[['gar ', ''], 'nichts '], 'keine Ergebnisse '], ['gefunden', 'finden können'], '.']
        ]

        output = generate_string(answers)
        return {'msg_speech': output, 'msg_text': output}

    definition = definition.replace('[[', '')
    definition = definition.replace(']]', '')
    definition = definition.replace('\n', '')

    definition = re.sub("\s*[\(\[].*?[\)\]]\s*", " ", definition)
    definition = re.sub("\s+", " ", definition)

    #definition = re.sub('#\s*\(.+\)\s*#U', ' ', definition)
    #definition = re.sub('#\s*\[.+\]\s*#U', ' ', definition)

    sentences = definition.split('. ')

    output = sentences[0]

    last_char = output[-1:]

    index = 1
    if len(sentences) > 1:
        while is_number(last_char) or len(output) < MIN_OUTPUT_LENGTH:
            output = output + '. ' + sentences[index]
            index = index + 1
            last_char = output[-1:]

    output = output + "."

    return {'msg_speech': output, 'msg_text': output}