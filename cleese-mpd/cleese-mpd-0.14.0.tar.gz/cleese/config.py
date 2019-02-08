from configparser import ConfigParser
from functools import lru_cache
from os.path import expanduser, join, exists


HOME = expanduser('~')
FILENAMES = [
    join(HOME, '.config', 'cleese', 'cleeserc'),
    join(HOME, '.cleeserc'),
]


@lru_cache()
def read_config():
    parser = ConfigParser()
    for filename in FILENAMES:
        if exists(filename):
            parser.read(filename)
            break
    else:
        raise FileNotFoundError()

    return parser
