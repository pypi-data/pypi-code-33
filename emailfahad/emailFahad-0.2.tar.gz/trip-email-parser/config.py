import os

from datetime import datetime
from lola.utils.config import LolaEnv


class Configuration(LolaEnv):
    OUTPUT_PATH = os.environ.get('OUTPUT_PATH', 'parsed_itineraries_{}.json'.format(datetime.utcnow().date()))
    USERNAME = os.environ.get('USERNAME')
    PASSWORD = os.environ.get('PASSWORD')