from .create_api import create_api
from .flask_tools import FlaskTools
from .version import __version__

# if somebody does "from somepackage import *", this is what they will
# be able to access:
__all__ = [
    'create_api',
    'FlaskTools'
]


def main():
    create_api()
