import pytest
from ioexplorer_dataloader.cli.common import logging


def test_error(capsys):
    with pytest.raises(SystemExit) as caught_exception:
        logging.error("Hello World")

    captured = capsys.readouterr()
    assert captured.out == "ERROR: Hello World\n"
    assert caught_exception.type == SystemExit
    assert caught_exception.value.code == 1


def test_success(capsys):
    logging.success("Hello World")
    captured = capsys.readouterr()
    assert captured.out == "SUCCESS: Hello World\n"


def test_info(capsys):
    logging.info("Hello World")
    captured = capsys.readouterr()
    assert captured.out == "INFO: Hello World\n"
