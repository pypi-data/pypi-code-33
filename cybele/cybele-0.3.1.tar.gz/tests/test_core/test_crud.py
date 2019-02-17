import os

import pytest
import pyperclip

from cybele.api import exceptions

from .fixtures import db

HERE = os.path.dirname(__file__)


def test_add_entry(db):
    db.add("new_entry", {"username": "new_username", "passphrase": "new_passphrase"})
    assert db.entries.get("new_entry") == {"username": "new_username", "passphrase": "new_passphrase"}


def test_edit_entry(db):
    db.edit("entry1", {"passphrase": "edited_passphrase"})
    assert db.entries.get("entry1") == {"username": "User1", "passphrase": "edited_passphrase"}


def test_edit_delete(db):
    db.delete("entry1")
    assert "entry1" not in db.entries


def test_raise_when_unavailable_on_add(db):
    with pytest.raises(exceptions.EntryNameNotAvailableError):
        db.add("entry1", {"username": "new_username", "passphrase": "new_passphrase"})


def test_raise_when_format_ko_on_add(db):
    with pytest.raises(exceptions.EntryFormatError):
        db.add("new_entry", {"not_good_key": "new_username", "passphrase": "new_passphrase"})


def test_raise_when_entry_not_found_on_edit(db):
    with pytest.raises(exceptions.EntryNotFoundError):
        db.edit("wrong_entry_name", {})


def test_raise_when_entry_not_found_on_delete(db):
    with pytest.raises(exceptions.EntryNotFoundError):
        db.delete("wrong_entry_name")
