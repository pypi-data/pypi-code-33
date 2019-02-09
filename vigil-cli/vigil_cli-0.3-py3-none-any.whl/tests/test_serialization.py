# Standard modules
import datetime
import json

# External dependencies
import pytest

# Local modules
from .context import vigil
from vigil.utils import serialization


class TestJSON:
    """
    Test JSON encoding and decoding.
    """

    def test_json_encoder(self, watch):
        """
        WatchEncoder should return a valid json.
        """
        dump = json.dumps(watch.as_dict(), cls=serialization.DatetimeEncoder)
        fields = ('name', 'url', 'content',
                  'diff', 'tolerance', 'interval', 'date')
        for field in fields:
            assert field in dump

    def test_deserialize(self, collection):
        """
        Should return watch corresponding to the list of attributes.
        """
        serialized = {'name': 'name',
                      'url': 'url',
                      'interval': {'days': 1},
                      'date': {'year': 2000,
                               'month': 12,
                               'day': 12},
                      'tolerance': 5,
                      'content': 'content',
                      'diff': 'diff'}
        deserialized = serialization.deserialize(serialized)
        deserialized = vigil.watch.Watch(**deserialized)
        assert isinstance(deserialized.interval, datetime.timedelta)
        assert isinstance(deserialized.date, datetime.datetime)
