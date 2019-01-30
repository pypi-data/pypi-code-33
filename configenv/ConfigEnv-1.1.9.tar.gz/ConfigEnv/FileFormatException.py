

class FileFormatException(Exception):
    """Base class for exceptions in this module."""
    def __init__(self):
        self.message = 'file format not suported'
