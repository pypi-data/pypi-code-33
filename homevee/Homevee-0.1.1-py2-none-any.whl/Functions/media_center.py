#!/usr/bin/python
# -*- coding: utf-8 -*-
import json
import urllib

from homevee.DeviceAPI import kodi_api
from homevee.Helper.helper_functions import has_permission

TYPE_KODI = "KODI"

def get_media_centers(username, db):
    media_centers = []

    with db:
        cur = db.cursor()

        cur.execute("SELECT *, MEDIA_CENTER.NAME as MEDIA_CENTER_NAME, ROOMS.NAME as ROOM_NAME FROM MEDIA_CENTER, ROOMS WHERE ROOMS.LOCATION = MEDIA_CENTER.LOCATION")

        for result in cur.fetchall():
            if(has_permission(username, result['LOCATION'], db)):
                item = {'name': result['MEDIA_CENTER_NAME'], 'type': result['TYPE'], 'id': result['ID'],
                        'location': result['LOCATION'], 'value': result['ROOM_NAME']}
                media_centers.append(item)

    return {'mediacenters': media_centers}

def media_remote_action(type, id, remoteaction, db):
    if type == TYPE_KODI:
        return kodi_api.media_remote_action(get_media_center_data(id, db), remoteaction)

def media_center_send_text(type, id, text, db):
    if type == TYPE_KODI:
        return kodi_api.send_text(get_media_center_data(id, db), text)

    return "nosuchtype"

def get_media_center_music(type, id, limit, offset, db):
    if type == TYPE_KODI:
        result = kodi_api.get_music(get_media_center_data(id, db), limit, offset)

        result = json.loads(result)

        songs = []

        song_array = result['result']['songs']

        for song in song_array:
            item = {'title': song['label'], 'artists': song['artist'], 'id': song['songid'], 'album': song['album']}
            songs.append(item)

        return {'songs': songs}

    return 'nosuchtype'

def get_media_center_artists(type, id, limit, offset, db):
    if type == TYPE_KODI:
        result = kodi_api.get_artists(get_media_center_data(id, db), limit, offset)

        result = json.loads(result)

        artists = []

        artist_array = result['result']['artists']

        for artist in artist_array:
            item = {'artist': artist['artist'], 'id': artist['artistid'], 'thumbnail': artist['thumbnail']}
            artists.append(item)

        return {'artists': artists}

    return 'nosuchtype'

def get_media_center_albums(type, id, limit, offset, db):
    if type == TYPE_KODI:
        result = kodi_api.get_albums(get_media_center_data(id, db), limit, offset)

        result = json.loads(result)

        albums = []

        album_array = result['result']['albums']

        for album in album_array:
            item = {'title': album['label'], 'artists': album['artist'], 'id': album['albumid'], 'thumbnail': album['thumbnail']}
            albums.append(item)

        return {'albums': albums}

    return 'nosuchtype'

def get_media_center_music_genres(type, id, limit, offset, db):
    if type == TYPE_KODI:
        result = kodi_api.get_music_genres(get_media_center_data(id, db), limit, offset)

        result = json.loads(result)

        genres = []

        genre_array = result['result']['genres']

        for genre in genre_array:
            item = {'title': genre['label'], 'id': genre['genreid'], 'thumbnail': genre['thumbnail']}
            genres.append(item)

        return {'genres': genres}

    return 'nosuchtype'

def get_media_center_movie_genres(type, id, limit, offset, db):
    if type == TYPE_KODI:
        result = kodi_api.get_movie_genres(get_media_center_data(id, db), limit, offset)

        print result

        result = json.loads(result)

        genres = []

        genre_array = result['result']['genres']

        for genre in genre_array:
            item = {'title': genre['label'], 'id': genre['genreid'], 'thumbnail': genre['thumbnail']}
            genres.append(item)

        return {'genres': genres}

    return 'nosuchtype'

def get_media_center_shows(type, id, limit, offset, db):
    if type == TYPE_KODI:
        result = kodi_api.get_tv_show(get_media_center_data(id, db), limit, offset)

        result = json.loads(result)

        tvshows = []

        tvshow_array = result['result']['tvshows']

        for tvshow in tvshow_array:

            thumbnail = tvshow['thumbnail']
            thumbnail = thumbnail.replace('image://', '')
            thumbnail = urllib.unquote(thumbnail).decode('utf8')

            item = {'title': tvshow['label'], 'genres': tvshow['genre'], 'id': tvshow['tvshowid'],
                    'year': ['year'], 'thumbnail': thumbnail}
            tvshows.append(item)

        return {'shows': tvshows}

    return 'nosuchtype'

def get_media_center_show_seasons(type, id, limit, offset, showid, db):
    if type == TYPE_KODI:
        result = kodi_api.get_tv_show_seasons(get_media_center_data(id, db), showid, limit, offset)

        result = json.loads(result)

        seasons = []

        season_array = result['result']['tvshows']

        for season in season_array:

            thumbnail = season['thumbnail']
            thumbnail = thumbnail.replace('image://', '')
            thumbnail = urllib.unquote(thumbnail).decode('utf8')

            item = {'title': season['label'], 'id': season['seasonid'], 'thumbnail': thumbnail}
            seasons.append(item)

        return {'seasons': seasons}

    return 'nosuchtype'

def get_media_center_show_episodes(type, id, limit, offset, showid, seasonid, db):
    return []

def get_media_center_movies(type, id, limit, offset, db):
    if type == TYPE_KODI:
        result = kodi_api.get_movies(get_media_center_data(id, db), limit, offset)

        result = json.loads(result)

        movies = []

        movie_array = result['result']['movies']

        for movie in movie_array:

            thumbnail = movie['thumbnail']
            thumbnail = thumbnail.replace('image://', '')
            thumbnail = urllib.unquote(thumbnail).decode('utf8')

            item = {'title': movie['label'], 'genres': movie['genre'], 'id': movie['movieid'],
                    'year': movie['year'], 'thumbnail': thumbnail}
            movies.append(item)

        return {'movies': movies}

    return 'nosuchtype'

def get_media_center_playing(type, id, db):
    return []

def get_media_menter_playing(type, id, db):
    return []

def get_media_center_data(id, db):
    with db:
        cur = db.cursor()

        cur.execute("SELECT * FROM MEDIA_CENTER WHERE ID == :id", {'id': id})

        result = cur.fetchone()

        return result