# Standard modules
import datetime
import os

# External dependencies
import tinydb
import pytest

# Local modules
from .context import vigil
from .mailbox import *
from vigil.watch import Watch
from vigil.config import Config
from vigil.collection import WatchCollection
from vigil.utils.serialization import DatetimeEncoder


@pytest.fixture
def watch(name='test', url='http://www.example.org'):
    """
    Return a mock Watch object for testing.
    """
    watch = Watch(name, url)
    watch.diff = None
    watch.content = 'content'
    watch.date = datetime.datetime(year=2000, month=1, day=1)
    return watch


@pytest.fixture
def nosave(monkeypatch):
    """
    Do not save config.
    """
    monkeypatch.setattr(Config, 'save', lambda x: True)


@pytest.fixture
def nonotify(monkeypatch):
    """
    Do not send notifications.
    """
    monkeypatch.setattr(WatchCollection, 'send_notification', lambda x: True)


@pytest.fixture
def testfile(tmpdir):
    """
    Return a temporary file for saving collection.
    """
    path = tmpdir.join('test.json')
    # Py.path doesn't work with builtin open(), so we convert it
    return str(path)


@pytest.fixture
def configfile(monkeypatch, tmpdir):
    path = str(tmpdir.join('config.yaml'))
    return path


@pytest.fixture
def config(configfile):
    """
    Setup mock config file.
    """
    return Config(configfile)


@pytest.fixture
def db(testfile, watch):
    db_ = tinydb.TinyDB(testfile, create_dirs=True, cls=DatetimeEncoder)
    db_.purge_tables()

    watch1 = watch.as_dict()
    watch1['name'] = 'html'
    watch1['url'] = 'http://httpbin.org/html'
    db_.insert(watch1)

    watch2 = watch.as_dict()
    watch2['name'] = 'xml'
    watch2['url'] = 'http://httpbin.org/xml'
    db_.insert(watch2)
    return db_


@pytest.fixture
def collection(db, config):
    """
    Setup mock WatchCollection for testing.
    """
    collection = WatchCollection(config)
    collection.db = db
    return collection
