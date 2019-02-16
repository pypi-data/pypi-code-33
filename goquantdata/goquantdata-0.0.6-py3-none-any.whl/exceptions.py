
class InputError(Exception):
    """User Input Parameter Error"""

    def __init__(self, message=None):
        self.message = message

    def __str__(self):
        if self.message:
            return str(self.message)
        return "An unknown error occurred."

class ApiError(Exception):
    """Represents an exception returned by the remote API."""
    def __init__(self, status, message=None):
        self.status = status
        self.message = message

    def __str__(self):
        if self.message is None:
            return self.status
        else:
            return "%s (%s)" % (self.status, self.message)