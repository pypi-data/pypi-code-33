from io import StringIO
from logging import StreamHandler, WARNING, Logger
from contextlib import contextmanager
from typing import Callable, ContextManager
import fastgenomics.deprecated as deprecated
import pytest


@pytest.fixture
def catch_log_warnings() -> Callable[[Logger], ContextManager[StreamHandler]]:
    @contextmanager
    def catcher(logger: Logger):
        handler = StreamHandler(StringIO())
        handler.setLevel(WARNING)
        logger.addHandler(handler)
        yield handler

    return catcher


@pytest.fixture
def local(monkeypatch, app_dir, data_root):
    """patches the paths for local testing"""
    with pytest.deprecated_call():
        deprecated.set_paths(app_dir, data_root)


@pytest.fixture
def fg_env(monkeypatch, app_dir, data_root):
    """sets app_dir and data_root by env-variables"""
    monkeypatch.setenv("FG_APP_DIR", str(app_dir))
    monkeypatch.setenv("FG_DATA_ROOT", str(data_root))


@pytest.fixture
def clear_output(data_root):
    """clear everything except of .gitignore"""
    for name in ["output", "summary"]:
        sub_dir = data_root / name
        for entry in sub_dir.glob("*.*"):
            if entry.name != ".gitignore":
                entry.unlink()
