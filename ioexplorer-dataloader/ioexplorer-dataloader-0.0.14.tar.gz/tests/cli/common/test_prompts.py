import pytest
from unittest import mock
from ioexplorer_dataloader.cli.common.prompts import ask_continue_on_invalid


def test_ask_continue_on_invalid():
    with mock.patch(
        "ioexplorer_dataloader.cli.common.prompts.prompt", lambda x: {"continue": True}
    ):
        ask_continue_on_invalid("Hello")

    with mock.patch(
        "ioexplorer_dataloader.cli.common.prompts.prompt", lambda x: {"continue": False}
    ):
        with pytest.raises(SystemExit) as caught_exception:
            ask_continue_on_invalid("Hello")
        assert caught_exception.type == SystemExit
        assert caught_exception.value.code == 1
