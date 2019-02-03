class TinyIntError(Exception):
    # constructor
    def __init__(self):
        self.message = "Your evaluation exceeds of 256 or is lower than 0, is not a TinyInt"

    # class override
    def __str__(self):
        return self.message
