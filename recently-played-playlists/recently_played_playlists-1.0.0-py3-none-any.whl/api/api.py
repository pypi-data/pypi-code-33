from recently_played_playlists.spotify.util import create_playlist, process_playlist

from flask import Flask, request

app = Flask(__name__)

# TODO: add validation? Probably more useful to add validation to what sends
# to the playlist-parser and trust that. Everything here is a string.
@app.route('/process_filter')
def process_filter():
    '''
    Processes a filter according to the playlist-parser spec and returns a list of
    spotify `song_id` that satisfy the filter.
    '''
    filter_args = dict()
    filter_args['username'] = request.args.get('username')
    filter_args['time_begin'] = request.args.get('time_begin')
    filter_args['time_end'] = request.args.get('time_end')
    filter_args['agby'] = request.args.get('agby')
    filter_args['limit'] = int(request.args.get('limit'))
    filter_args['saved'] = int(request.args.get('saved'))
    filter_args['count'] = int(request.args.get('count'))
    filter_args['comparator'] = int(request.args.get('comparator'))
    filter_args['release_start'] = request.args.get('release_start')
    filter_args['release_end'] = request.args.get('release_end')

    return process_playlist(filter_args)

'''
Query params: username, playlist_name
Post body: csv of track_ids

# possible TODO: parameterize for public/private and collaborative
'''
@app.route('/make_playlist', methods=['POST'])
def make_playlist():
    track_ids_csv_string = str(request.data.decode("utf-8"))
    track_ids = track_ids_csv_string.split(',')
    username = request.args.get('username')
    playlist_name = request.args.get('playlist_name')
    description = request.args.get('description')
    print('Num tracks sent to /make_playlist')

    # If there are no tracks, track_ids has length 1 and an empty first element.
    if len(track_ids) == 1 and track_ids[0] == '':
        return 'No tracks identified to fit this playlist, returning w/o a playlist\n'

    print(track_ids)
    print(len(track_ids))

    create_playlist(username, track_ids, playlist_name, description)

    return 'great!'

def main():
    app.run()
