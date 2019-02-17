import json
import os

import pyperclip

from ..aes import AESCipher
from ..aes.exception import WrongPassphraseError
from .exceptions import DBNotFoundError, EntryNameNotAvailableError, EntryFormatError, EntryNotFoundError
from .utils import flush_clipboard


class Database:
    def __init__(self, path_to_db, key):
        self._check_db_exists(path_to_db)
        self.cipher = AESCipher(key)
        self.path_to_db = path_to_db

        self.entries = self.load(path_to_db)

    def add(self, entry_name, entry):
        self._check_entryname_available(entry_name)
        self._check_entry(entry)
        self.entries[entry_name] = entry

    def edit(self, entry_name, updates):
        self._check_entry_exists(entry_name)
        self.entries[entry_name].update(updates)
    
    def delete(self, entry_name):
        self._check_entry_exists(entry_name)
        del self.entries[entry_name]

    def load(self, path):
        with open(path, "r") as f:
            encrypted_data = f.read()
        try:
            entries_dumps = self.cipher.decrypt(encrypted_data)
            entries = json.loads(entries_dumps)
            return entries
        except (json.JSONDecodeError, UnicodeDecodeError) as exc:
            raise WrongPassphraseError("Wrong passphrase")

    def dump(self, path):
        entries_dumps = json.dumps(self.entries)
        encrypted_data = self.cipher.encrypt(entries_dumps)
        with open(path, "w") as f:
            f.write(encrypted_data)

    @flush_clipboard(after=10)
    def clip_passphrase(self, entry_name):
        self._check_entry_exists(entry_name)
        passphrase = self.entries[entry_name].get("passphrase")
        pyperclip.copy(passphrase)

    @flush_clipboard(after=10)
    def clip_username(self, entry_name):
        self._check_entry_exists(entry_name)
        username = self.entries[entry_name].get("username")
        pyperclip.copy(username)

    def _check_db_exists(self, path_to_db):
        if not os.path.exists(path_to_db):
            raise DBNotFoundError(f"No such DB file : '{path_to_db}'.")

    def _check_entry_exists(self, entry_name):
        if entry_name not in self.entries:
            raise EntryNotFoundError(f"Entry named '{entry_name}' can't be found in DB.")

    def _check_entryname_available(self, entry_name):
        if entry_name in self.entries:
            raise EntryNameNotAvailableError(f"Entry named '{entry_name}' already exists.")

    @staticmethod
    def _check_entry(entry):
        if not all(key in entry for key in ["username", "passphrase"]):
            raise EntryFormatError("Entry must have a 'username' & 'passphrase' key.")
