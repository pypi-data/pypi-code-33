""" The core package for all my flask apps
    ..moduleauthor:: Jordan Morris
    keywords: flask
    author: Jordan Taylor Morris
"""

# __version__ = '0.0.5'
__versioning__ = 'build-id'
__liscense__ = 'MIT'
__title__ = 'jtmorrisbytes-flask-api'
__url__ = 'https://www.github.com/jtmorrisbytes'
__author__ = "Jordan Taylor Morris"
__email__ = "jthecybertinkerer@gmail.com"
from . import factories
from . import models
from . import views
from . import controllers



def main():
    " this starts the flask app"
    factories.appfactory.create_app()