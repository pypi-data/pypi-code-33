import os
from tempfile import mkstemp

import pytest

from pyqalx import Qalx


def get_qalx_class():
    """
    Helper function for getting our qalx test class
    :return: TestQalx class
    """
    log_handle, temp_log_path = mkstemp()
    os.close(log_handle)

    class TestQalx(Qalx):

        def get_context(self):
            return dict(
                TOKEN="",  # no token is available by default
                QALX_API_FAIL_SILENT=False,
                # if True then API calls which throw HTTP errors won't raise exceptions
                MSG_WAITTIMESECONDS=20,
                # calls to the remote queue will not return for this long
                MSG_BLACKOUTSECONDS=30,
                # messages must be removed from the queue within this time after reading
                LOG_FILE_PATH=temp_log_path,
                LOGGING_LEVEL="ERROR"
            )

    return TestQalx


@pytest.fixture()
def qalx_class():
    return get_qalx_class()


@pytest.fixture()
def qalx():
    return get_qalx_class()(skip_ini=True)


@pytest.fixture
def fake_environ(mocker):
    mocker.patch.dict('pyqalx.config.os.environ',
                      QALX_BOT_THING="A BOT THING",
                      QALX_USER_THING="A USER THING",
                      SOME_OTHER_THING="SECRET")
    return mocker
