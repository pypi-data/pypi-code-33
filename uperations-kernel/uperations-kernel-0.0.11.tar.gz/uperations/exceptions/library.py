
class LibraryException(Exception):
    def __init__(self, message):

        # Call the base class constructor with the parameters it needs
        super(LibraryException, self).__init__("Uperation library: %s " % (message))

class LibraryNotFound(LibraryException):
    def __init__(self, message):

        # Call the base class constructor with the parameters it needs
        super(LibraryNotFound, self).__init__("Uperation library not found: %s" % (message))