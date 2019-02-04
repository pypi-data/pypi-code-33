from flask import Flask
from flask_sockets import Sockets

from . import converters


def create_app():
    app = Flask('sonoff')
    app.url_map.converters.update(**converters.converters)
    return app
