class NoUnprocessedCorpus(Exception):
    """Raised when accessing an unprocessed corpus before it exists."""
    def __init__(self, message="No unprocessed corpus. Try adding one."):
        super().__init__(message)


class AccessViolationException(Exception):
    """Raised when setting something in a way you shouldn't."""
    def __init__(self, message="Access violation."):
        super().__init__(message)

    def __repr__(self):
        return f"{self.__class__.__name__}(Exception)"


class InvalidCorpusFile(Exception):
    """Raised when passing an invalid file."""
    def __init__(self, message="Invalid corpus file."):
        super().__init__(message)

    def __repr__(self):
        return f"{self.__class__.__name__}(Exception)"


class NoCorpus(Exception):
    """Raised when attempting to set up automatically without a corpus."""
    def __init__(self, message="Invalid corpus or corpus file."):
        super().__init__(message)

    def __repr__(self):
        return f"{self.__class__.__name__}(Exception)"
