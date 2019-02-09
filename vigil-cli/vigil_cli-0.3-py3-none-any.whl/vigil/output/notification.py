""" Handle desktop notifications."""
# External dependencies
import plyer

# Local modules
from vigil import output


class Notification(output.Output):  # pylint: disable=too-few-public-methods
    """
    Output to system notifications.

    Attributes:
        subject (str): Title of notification.
        content (str): Content of notification.
        config (dict): Configuration.
    """
    only_url = True

    def send(self):
        try:
            plyer.notification.notify(self.subject, self.content, 'Vigil')
            return True
        except OSError:
            return False
