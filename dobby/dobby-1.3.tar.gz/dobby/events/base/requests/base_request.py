class BaseRequest:
    """A base class for all request types"""

    def __init__(self, data={}):
        """Initialize the base request

                Arguments:
                    data {object} -- request data (default: {})
        """

        self.data = data
