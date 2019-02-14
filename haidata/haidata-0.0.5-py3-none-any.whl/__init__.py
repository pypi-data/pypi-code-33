"""A haidata demonstration vehicle.

.. moduleauthor:: Hans Roggeman <hansroggeman2@gmail.com>

"""
__version__ = '0.0.5'


import os
import sys

myPath = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, myPath)
sys.path.insert(0, os.path.join(myPath, 'config'))
sys.path.insert(0, os.path.join(myPath, 'tests'))


def start():
    # "This starts this module running ..."
    pass
