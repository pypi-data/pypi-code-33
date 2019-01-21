"""
Module providing logger configurations.
"""
import logging
import sys
import os

LOGGER = logging.getLogger('mona-logger')
if os.environ.get('MONA_LOGGING_LEVEL'):
    try:
        LOGGER.setLevel(int(os.environ.get('MONA_LOGGING_LEVEL')))
    except ValueError:
        LOGGER.error('Tried to set mona logging level to unknown level')

if os.environ.get('MONA_PRINT_LOGS'):
    _handler = logging.StreamHandler(sys.stdout)
    _handler.setLevel(logging.DEBUG)
    _formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    _handler.setFormatter(_formatter)
    LOGGER.addHandler(_handler)
