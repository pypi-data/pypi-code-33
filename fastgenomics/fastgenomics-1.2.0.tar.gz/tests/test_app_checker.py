import logging
import jsonschema
import pytest

from fastgenomics.app import FGApp
from fastgenomics.process import FGProcess


def test_fgapp(app_dir):
    FGApp(app_dir)


def test_app_validation_error(app_dir_validation_error):
    with pytest.raises(jsonschema.ValidationError):
        FGApp(app_dir_validation_error)


def test_app_runtime_error(app_dir_runtime_error):
    with pytest.raises(RuntimeError):
        FGApp(app_dir_runtime_error)


def test_app_file_not_found(app_dir_missing_files):
    with pytest.raises(FileNotFoundError) as e:
        FGApp(app_dir_missing_files)
    assert "LICENSE" in str(e.value)
    assert "LICENSE-THIRD-PARTY" in str(e.value)
    assert "manifest.json" in str(e.value)


def test_app_non_existing(app_dir_non_existing):
    with pytest.raises(FileNotFoundError) as e:
        FGApp(app_dir_non_existing)
    assert "Could not find the App directory" in str(e.value)


def test_fgprocess_1(app_dir, data_root, caplog):
    caplog.set_level(logging.DEBUG)
    FGProcess(app_dir, data_root)
    assert any(
        ["Parameters" in x.message for x in caplog.records]
    ), "Parameter logs are not set"


def test_fgprocess_2(app_dir, data_root_2, caplog):
    caplog.set_level(logging.DEBUG)
    FGProcess(app_dir, data_root_2)
    assert any(
        ["Parameters" in x.message for x in caplog.records]
    ), "Parameter logs are not set"
