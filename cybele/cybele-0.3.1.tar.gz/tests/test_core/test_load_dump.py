import os
import tempfile

import pytest

from cybele.aes import passphrase_to_key
from cybele.aes.exception import WrongPassphraseError
from cybele.api.core import Database
from cybele.api import exceptions

from .fixtures import db

HERE = os.path.dirname(__file__)


def test_raise_no_such_db():
    with pytest.raises(exceptions.DBNotFoundError):
        _ = Database("fake/path/to/db", key=None)


def test_raise_when_wrong_passphrase():
    passphrase = "wrong_passphrase"
    key = passphrase_to_key(passphrase)
    path_to_db = os.path.join(HERE, "..", "data", "encrypted_fake_entries.json")
    with pytest.raises(WrongPassphraseError):
        db = Database(path_to_db, key)


def test_load_entries(db):
    expected_entries = {
        'entry1': {'username': 'User1', 'passphrase': 'passphrase1'},
        'entry2': {'username': 'User2', 'passphrase': 'passphrase2'}
    }
    assert db.entries == expected_entries


def test_dump_entries(db):
    with tempfile.NamedTemporaryFile() as tmp:
        db.dump(tmp.name)
        assert db.load(tmp.name) == db.entries
