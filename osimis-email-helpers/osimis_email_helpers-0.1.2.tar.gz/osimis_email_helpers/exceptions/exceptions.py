class EmailHelpersException(Exception):

    def __init__(self, msg = "Unexpected error in EmailHelpers", innerException:Exception = None):
        self.msg = msg
        self.innerException = innerException

    def __str__(self):
        return "EmailHelpers exception: {msg}, inner exception: {innerException}".format(msg = self.msg, innerException = str(self.innerException))