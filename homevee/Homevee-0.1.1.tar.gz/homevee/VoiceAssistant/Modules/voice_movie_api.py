#!/usr/bin/python
# -*- coding: utf-8 -*-
import urllib2

from homevee.Manager.api_key import get_api_key
from homevee.VoiceAssistant.voice_patterns import PATTERN_MOVIE_RATING


def get_pattern(db):
    return PATTERN_MOVIE_RATING

def get_label():
    return "movierating"

def run_command(username, text, context, db):
    return get_movie_rating(username, text, context, db)

def get_movie_rating(username, text, context, db):
    api_key = get_api_key('TMDB', db)

    words = text.split(" ")

    query = None

    is_query = False

    film_index = -1

    for i in range(0, len(words)):
        word = words[i]
        if is_query:
            if query is None:
                query = word.capitalize()
            else:
                query = query + " " + word.capitalize()

        if word == "film":
            if not is_query:
                film_index = i
            is_query = True

        if is_query and i > film_index and query != None:
            if word == "gut" or word == "schlecht":
                break

    #url = 'https://api.themoviedb.org/3/movie/'+movie_id+'?api_key='+api_key+'&language=de/'
    #response = urllib2.urlopen(url).read()
    #print(response)

    #return {'msg_speech': output, 'msg_text': output}