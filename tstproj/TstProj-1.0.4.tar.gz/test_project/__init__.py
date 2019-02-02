from configparser import ConfigParser
from pathlib import Path

if __name__ == '__main__':
    user_config = str(Path().cwd() / 'data' / 'user.ini')

    parser = ConfigParser()
    parser.read(user_config)
    print(dict(parser["info"]))
