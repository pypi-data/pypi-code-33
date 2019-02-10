bge_modules = 'aud', 'bge', 'bgl', 'blf', 'mathutils'

from os.path import dirname
path = dirname(__file__) # Path of the bgez folder
from .system import project
del dirname

from bgez.core.logging import logger

__all__ = [
    'bge_modules',
    'path',
    'project',
    'logger',
    'system',
]

from bgez.components import Launcher
