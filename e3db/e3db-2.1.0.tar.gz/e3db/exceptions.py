class APIError(Exception):
    def __init__(self, text):
        Exception.__init__(self, "Error during API operation: {0}".format(text))


class QueryError(APIError):
    def __init__(self, record_id):
        APIError.__init__(self, "Error during query: {0}".format(record_id))


class LookupError(APIError):
    def __init__(self, text):
        APIError.__init__(self, "Error during lookup: {0}".format(text))


class ConflictError(APIError):
    def __init__(self, text):
        APIError.__init__(self, "Conflict error: {0}".format(text))


class CryptoError(Exception):
    def __init__(self, text):
        Exception.__init__(self, "Error during Crypto operation: {0}".format(text))
