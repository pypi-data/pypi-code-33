"""A collection of exceptions that could be trown by the code."""


class IsABookException(Exception):
    """Exception to be trown if a book is encountert with multiple articles."""


class DocumentNotFound(Exception):
    """Exception to be trown if no document can be found."""
