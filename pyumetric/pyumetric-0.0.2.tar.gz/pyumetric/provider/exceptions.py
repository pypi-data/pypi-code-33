"""
Custom Exceptions
"""


class NewRelicApiException(Exception):
    def __init__(self, message):
        super(NewRelicApiException, self).__init__()


class NewRelicInvalidApiKeyException(NewRelicApiException):
    def __init__(self, message):
        super(NewRelicInvalidApiKeyException, self).__init__(message)


class NewRelicInvalidParameterException(NewRelicApiException):
    def __init__(self, message):
        super(NewRelicInvalidParameterException, self).__init__(message)
