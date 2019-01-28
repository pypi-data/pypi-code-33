class ValidationError(Exception):
    """Generic validation exception"""

    def __init__(self, message="The request's execution was not initiated due to invalid content", errors=[]):
        """Initialize the validation error

        Arguments:
            message {string} -- the message describing the problem

        Keyword Arguments:
            errors {list} -- additional errors (default: {[]})
        """

        super().__init__(message)
        self.message = message
        self.errors = []
