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


def init_app():
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
		app.config.update(os.environ)
		app.config.update(config)
		return app
	except:
		log.warning("There is no configuration found")
		raise


def enable_consul(application: Flask, config):
	consul.init_app(application)
	consul.load_config(namespace=config['namespace'])
	config.pop('namespace')
	consul.register(**config)


def enable_cache(application: Flask):
	cache.init_app(application, application.config)
	

def enable_database(application: Flask):
	db.init_app(application)
