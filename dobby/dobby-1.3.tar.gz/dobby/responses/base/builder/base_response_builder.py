class BaseResponseBuilder:
    """A base class for all result builders"""

    def __init__(self):
        # TODO: do we need any kind of extra steps here?
        pass

    def create_response(self, result):
        """The build method construct a response from a result object."""

        raise NotImplementedError
