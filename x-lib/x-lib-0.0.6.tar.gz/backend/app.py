import codecs
import json
import os

from flask import Flask
from flask_caching import Cache
from flask_sqlalchemy import SQLAlchemy

from .consul import Consulate
from .logger import logging

log = logging.getLogger(__name__)

DEFAULT_CONFIG = 'application'
db = SQLAlchemy()
consul = Consulate()
cache = Cache()
app = Flask(__name__)


def create_app(configure=None):
    try:
        if os.getenv('flask_profiles_active', ''):
            json_file = open(DEFAULT_CONFIG + '_' + os.getenv('flask_profiles_active', '') + '.json', 'rb')
            reader = codecs.getreader('utf-8')
            config = json.load(reader(json_file))
            json_file.close()
        else:
            json_file = open(DEFAULT_CONFIG + '.json', 'rb')
            reader = codecs.getreader('utf-8')
            config = json.load(reader(json_file))
            json_file.close()
        app.config.update(config)
        app.config.update(configure)
        json_file.close()
        consul.init_app(app)
        consul.load_config(namespace=config['namespace'])
        config.pop('namespace')
        consul.register(**config)
        cache.init_app(app, app.config)
    except:
        log.info("Consulate is not running")
        pass
    return app