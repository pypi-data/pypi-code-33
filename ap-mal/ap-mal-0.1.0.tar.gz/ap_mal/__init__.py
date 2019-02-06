import argparse

from .base import Service
from .ap import AnimePlanet
from .mal import MyAnimeList

__version__ = '0.1.0'
DEBUG = 0


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        'ap-mal', description='Import and Export anime and manga lists '
                              'on Anime-Planet and MyAnimeList')
    parser.add_argument(
        '--version', action='version',
        version=f'ap-mal {__version__}')
    parser.add_argument(
        '-v', action='count',
        help='Increase output verbosity (e.g. -vv, -vvv)')
    parser.add_argument(
        '-f', type=str, default=None, metavar='FILE', dest='FILE',
        help='Path to a JSON file with data to use during an import'
    )
    parser.add_argument(
        '-l', type=str, default='all', metavar='LIST', dest='LIST_TYPE',
        choices=['anime', 'manga', 'ln', 'all'],
        help='Type of list to export (defaults to all)'
    )
    group = parser.add_mutually_exclusive_group(required=True)
    services = ['ap', 'anime-planet', 'mal', 'myanimelist']
    group.add_argument(
        '-i', type=str, default=None, metavar='SERVICE',
        dest='IMPORT', choices=services,
        help='Import data to the named service from either an exported '
             'file or fresh data exported from another service'
    )
    group.add_argument(
        '-e', type=str, default=None, metavar='SERVICE',
        dest='EXPORT', choices=services,
        help='Service to export from. Data will be saved to: '
             '<service>_<timestamp>_<list-type>-list_export.json'
    )
    arguments = parser.parse_args()
    if arguments.v:
        global DEBUG
        DEBUG = arguments.debug
    if DEBUG >= 2:
        print(f"Arguments: {str(arguments)}")
    return arguments
