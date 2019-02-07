import calendar
import time

from recently_played_playlists.spotify.util import get_spotify_client_for_username
from recently_played_playlists.db.db import get_all_users, get_time_of_last_track_play, save_track_if_not_exists, save_played_song, update_time_of_last_track_play

def iso_8601_timestamp_with_millis_and_timezone_to_seconds_since_epoch(timestamp):
    '''
    https://wiki.python.org/moin/WorkingWithTime
      "Note that this method does not handle time zones, so trying to parse 2004-06-03T12:34:56-0700 or 
      2004-06-03T12:34:56Z will fail. This is a fundamental limitation of time.strptime for which there is no easy workaround."

      Spotify returns timestamps in the form 2004-06-03T12:34:56.123Z, which applies to this format. I've also learned that sometimes no millis are attached!

      So, cut off the millis and timestamp, and convert to seconds since epoch.
    '''
    return calendar.timegm(time.strptime(timestamp.replace('Z', '', 1).rsplit('.')[0], "%Y-%m-%dT%H:%M:%S"))

def find_latest_timestamp(played_tracks):
    latest_timestamp = -1
    for x in played_tracks:
        if x['played_at'] > latest_timestamp:
            latest_timestamp = x['played_at']

    return latest_timestamp
    
def parse_recently_played_api_response(response):
    '''
    Returns list of dict's with the following keys:
      - name
      - uri
      - id
      - duration_ms
      - played_at
    '''
    list_of_tracks = []

    for k, api_response_tracks in response.items():
        if k == 'items':
            for api_response_track in api_response_tracks:
                '''
                Fields I may care about in the future:
                    track['track']['artists'] - list
                '''
                played_track = dict()

                played_track['name'] = api_response_track['track']['name']
                played_track['uri'] = api_response_track['track']['uri']
                played_track['id'] = api_response_track['track']['id']
                played_track['duration_ms'] = api_response_track['track']['duration_ms']
                played_track['played_at'] = iso_8601_timestamp_with_millis_and_timezone_to_seconds_since_epoch(api_response_track['played_at'])
                list_of_tracks.append(played_track)

    return list_of_tracks

def call_recently_played_endpoint(username):
    spotify = get_spotify_client_for_username(username)
    response = spotify.current_user_recently_played()
    return parse_recently_played_api_response(response)

def save_recently_played_tracks(username):
    '''
    - Fetch spotify tokens for `username`
    - Query spotify API for recently played tracks for `username`
    - Add each new track to the tracks table
    - Add each new played track to the songs_played table

    misc:
      Spotify does support an 'after' timestamp on the get-recently-played endpoint, however, 
      if no songs have been played since 'after', spotify returns 1 song, the most recently
      played one for the user. For this reason, do not use the 'after' parameter, and use the 
      `time_of_last_track_played` field in the database to determine whether the song is 'new' or not.
    '''
    time_of_last_track_played = get_time_of_last_track_play(username)

    played_tracks = call_recently_played_endpoint(username)

    num_new_track_plays = 0
    # Save track plays that are newer than `time_of_last_track_played`
    for x in played_tracks:
        if int(x['played_at']) > int(time_of_last_track_played):
            save_track_if_not_exists(x)
            save_played_song(username, x['uri'], x['played_at'])
            num_new_track_plays += 1

    # Update time of last play.
    # Find the max time value ourselves. Don't rely on spotify
    # returning the tracks in the order they were played.
    latest_song_play = find_latest_timestamp(played_tracks)
    update_time_of_last_track_play(username, latest_song_play)

    print(f'Saved {num_new_track_plays} to songs_played table for {username}')

    return 0


def main():
    usernames = get_all_users()
    for user in usernames:
        save_recently_played_tracks(user)
