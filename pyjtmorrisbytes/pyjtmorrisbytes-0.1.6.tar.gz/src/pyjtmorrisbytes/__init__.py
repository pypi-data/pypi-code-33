""" The core package for all my flask apps
    ..moduleauthor:: Jordan Morris
    keywords: flask
    author: Jordan Taylor Morris
"""

__version__ = '0.1.6'
# __versioning__ = 'branch(dev,master):{major}.{minor}.{patch}'
__liscense__ = 'MIT'
__title__ = 'pyjtmorrisbytes'
__srcurl__ = 'https://www.github.com/pyjtmorrisbytes/'
__url__ = 'https://www.jtmorrisbytes.com/'
__author__ = "Jordan Taylor Morris jthecybertinkerer@gmail.com"
# __email__ = "jthecybertinkerer@gmail.com"
from . import factories
from . import models
from . import views
from . import controllers
from . import config