"""Definitions related to searching locally."""

import difflib
import glob
import os


class SearchLocal:
    """Search the file locally."""

    def __init__(self, dir, kw, length):
        """Init the stuff."""
        dir = os.path.expanduser(dir)
        self.dir = dir
        self.kw = kw
        self.length = length

    def Search_Song(self):
        """Search the song in the directory."""
        # Get the list of songs in dir
        os.chdir(self.dir)
        songs = glob.glob('*.mp3')
        results = difflib.get_close_matches(self.kw, songs, len(songs), self.length)
        return results


def main(kw='Shape Of You'):
    """Run on program call."""
    search = SearchLocal('~/Music', 'You', 0.3)
    res = search.Search_Song()
    if len(res) != 0:
        for songs in res:
            if kw in songs:
                print(songs)
                break


if __name__ == '__main__':
    main()
