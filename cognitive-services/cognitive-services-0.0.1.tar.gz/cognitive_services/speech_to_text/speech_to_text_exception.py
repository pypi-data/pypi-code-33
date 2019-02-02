

class SpeechToTextException(Exception):

    def __init__(self, code, message):
        self.code = code
        self.message = message

    def __str__(self):
        msg = 'Error: ' + str(self.message) + ', Code: ' + str(self.code)
        return msg
