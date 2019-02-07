import os

from dotenv import load_dotenv, find_dotenv
from spotipy.oauth2 import SpotifyClientCredentials
import spotipy

from recently_played_playlists.db.db import get_db_creds
from recently_played_playlists.db.db import map_playlist_params_to_query
from recently_played_playlists.db.db import exec_process_playlist_query

def get_spotify_app_creds():
    # Ensure secrets are loaded
    load_dotenv(find_dotenv())

    creds = {}
    creds['SPOTIFY_CLIENT_ID'] = os.getenv('SPOTIFY_CLIENT_ID')
    creds['SPOTIFY_CLIENT_SECRET'] = os.getenv('SPOTIFY_CLIENT_SECRET')

    return creds

def get_spotify_client_for_username(username):
    credentials = SpotifyClientCredentials(
        username, 
        db_creds=get_db_creds(),
        spotify_app_creds=get_spotify_app_creds()
    )

    return spotipy.Spotify(client_credentials_manager=credentials)

def process_playlist(parameters):
    playlist_query = map_playlist_params_to_query(parameters)
    tracks = exec_process_playlist_query(playlist_query)

    saved = parameters['saved']

    print('Got this many tracks back from the query')
    print(tracks)
    print(len(tracks))

    # If the saved parameter was set, filter for it.
    if saved == 0 or saved == 1:
        tracks = check_tracks_saved(parameters['username'], tracks, saved)
    print('Sending back this many tracks from /process_filter')
    print(len(tracks))

    return ','.join(tracks)

def check_tracks_saved(username, track_ids, saved):
    '''
    Filters track_ids for either being saved or not saved in a user's library according to `saved`.

    username  - user's username in db
    track_ids - list of spotify track id's
    saved     - string of 0 or 1. If 0, return tracks that are not in a user's library. If 1, return
            tracks that are in a user's library.
    '''
    spotify = get_spotify_client_for_username(username)

    list_of_bools_in_order_of_track_ids = spotify.current_user_saved_tracks_contains(track_ids)

    assert (len(list_of_bools_in_order_of_track_ids) == len(track_ids))
    print(list_of_bools_in_order_of_track_ids)

    value = None
    if saved == 1:
        value = True
    elif saved == 0:
        value = False

    return filter_lists_based_on_value(value, track_ids, list_of_bools_in_order_of_track_ids)

def create_playlist(username, track_ids, playlist_name, description):
    spotify = get_spotify_client_for_username(username)
    print('track ids:')
    print(track_ids)

    spotify_user_data = spotify.me()
    spotify_user_id = spotify_user_data['id']

    playlist_is_public = True

    playlist = spotify.user_playlist_create(spotify_user_id, playlist_name, playlist_is_public, description)
    if playlist is None:
        raise Exception('Playlist not created successfully')

    playlist_id = playlist['id']
    val = spotify.user_playlist_add_tracks(spotify_user_id, playlist_id, track_ids)

    if val is None:
        raise Exception('Error adding tracks to playlist')

    return 'Success'

def filter_lists_based_on_value(value, tracks, bools):
    assert(len(tracks) == len(bools))

    rv = []
    for x in range(0,len(tracks)):
        if bools[x] == value:
            rv.append(tracks[x])
    return rv
