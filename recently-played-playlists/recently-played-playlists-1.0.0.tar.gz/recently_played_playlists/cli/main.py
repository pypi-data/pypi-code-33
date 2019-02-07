import sys

from recently_played_playlists.spotify import save_recently_played_tracks
from recently_played_playlists.api import api

def main():
    if sys.argv[1] == 'save-played-tracks':
        save_recently_played_tracks.main()
    elif sys.argv[1] == 'api':
        api.main()
    else:
        print('ERROR: subcommands are: api, save-played-tracks')
