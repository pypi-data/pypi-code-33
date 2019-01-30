class PushResponseError(Exception):
    """Base class for all push reponse errors"""

    def __init__(self, push_response):
        if push_response.message:
            self.message = push_response.message
        else:
            self.message = "Unknown push response error"
        super(PushResponseError, self).__init__(self.message)

        self.push_response = push_response


class DeviceNotRegisteredError(PushResponseError):
    """Raised when the push token is invalid

    To handle this error, you should stop sending messages to this token.
    """

    pass


class MessageTooBigError(PushResponseError):
    """Raised when the notification was too large.

    On Android and iOS, the total payload must be at most 4096 bytes.
    """

    pass


class MessageRateExceededError(PushResponseError):
    """Raised when you are sending messages too frequently to a device

    You should implement exponential backoff and slowly retry sending messages.
    """

    pass


class PushServerError(Exception):
    """Raised when the push token server is not behaving as expected

    For example, invalid push notification arguments result in a different
    style of error. Instead of a "data" array containing errors per
    notification, an "error" array is returned.

    {"errors": [
      {"code": "API_ERROR",
       "message": "child \"to\" fails because [\"to\" must be a string]. \"value\" must be an array."
      }
    ]}
    """

    def __init__(self, message, response, response_data=None, errors=None):
        self.message = message
        self.response = response
        self.response_data = response_data
        self.errors = errors
        super(PushServerError, self).__init__(self.message)
