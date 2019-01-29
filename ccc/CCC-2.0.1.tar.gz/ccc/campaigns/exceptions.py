class Error(Exception):
    """Base class for other exceptions"""


class ThrotleLimitException(Error):
    """Handle Throttle Error"""
    error_code = 1501

    def __init__(self, *args, **kwargs):
        message = "Throttle Limit hit"
        # Call the base class constructor with the parameters it needs
        super(ThrotleLimitException, self).__init__(message)
        self.code = self.error_code
        self.message = message
