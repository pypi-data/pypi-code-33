from configparser import ConfigParser
from pathlib import Path

user_config = str(Path().cwd() / 'data' / 'user.ini')

parser = ConfigParser()
parser.read(user_config)
print(dict(parser["info"]))
