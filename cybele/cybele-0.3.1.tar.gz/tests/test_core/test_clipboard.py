from unittest.mock import patch

import pyperclip
import pytest

from .fixtures import db


def pyperclip_available():
    try:
        pyperclip.paste()
        return False
    except pyperclip.PyperclipException as exc:
        return True


@pytest.mark.skipif(pyperclip_available(), reason="pyperclip not available on system")
def test_pyperclip_dependency():
    pyperclip.copy("to be copied")
    assert pyperclip.paste() == "to be copied"


@pytest.mark.skipif(pyperclip_available(), reason="pyperclip not available on system")
@patch("cybele.api.utils.tqdm", return_value=[])
def test_flush_on_clip_username(tqdm_mock, db):
    pyperclip.copy("supposed to be erased")
    db.clip_username("entry1")
    assert pyperclip.paste() == ""


@pytest.mark.skipif(pyperclip_available(), reason="pyperclip not available on system")
@patch("cybele.api.utils.tqdm", return_value=[])
def test_flush_on_clip_passphrase(tqdm_mock, db):
    pyperclip.copy("supposed to be erased")
    db.clip_passphrase("entry1")
    assert pyperclip.paste() == ""


@pytest.mark.skipif(pyperclip_available(), reason="pyperclip not available on system")
@patch("cybele.api.utils.tqdm", return_value=range(10))
@patch("cybele.api.utils.time.sleep", side_effect=Exception())
def test_flush_even_if_exception(sleep_mock, tqdm_mock, db):
    pyperclip.copy("supposed to be erased")
    with pytest.raises(Exception):
        db.clip_username("entry1")
    assert pyperclip.paste() == ""
