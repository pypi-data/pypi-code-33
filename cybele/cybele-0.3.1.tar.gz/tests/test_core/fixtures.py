import os
import pytest

from cybele.aes.cipher import passphrase_to_key
from cybele.api.core import Database

HERE = os.path.dirname(__file__)


@pytest.fixture
def db():
    passphrase = "passphrase"
    key = passphrase_to_key(passphrase)
    path_to_db = os.path.join(HERE, "..", "data", "encrypted_fake_entries.json")
    db = Database(path_to_db, key)
    return db
