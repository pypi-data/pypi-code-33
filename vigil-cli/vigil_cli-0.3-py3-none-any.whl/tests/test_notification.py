# External depencies
import pytest

# Local modules
from .context import vigil
from vigil.output import notification


class TestNotification:
    """
    Tests output to system notifications.
    """

    def test_send(self):
        """
        Notification should not raise any exceptions.
        """
        try:
            notification.Notification('Subject', 'Content', '{}').send()
        except NotImplementedError:
            # When running in docker on CI
            pass
