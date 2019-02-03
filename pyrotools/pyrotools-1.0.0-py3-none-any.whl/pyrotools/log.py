class Log(object):
    DEBUG = 'd'
    WARNING = 'w'
    ERROR = 'e'

    __messages = {DEBUG: [], WARNING: [], ERROR: []}

    @staticmethod
    def __append_message(channel, message):
        # print(channel, ": ", message)
        Log.__messages[channel].append(message)

    @staticmethod
    def d(message):
        Log.__append_message(Log.DEBUG, message)

    @staticmethod
    def w(message):
        Log.__append_message(Log.WARNING, message)

    @staticmethod
    def e(message):
        Log.__append_message(Log.ERROR, message)

    @staticmethod
    def get_debug():
        return Log.DEBUG

    @staticmethod
    def get_warning():
        return Log.WARNING

    @staticmethod
    def get_error():
        return Log.ERROR
