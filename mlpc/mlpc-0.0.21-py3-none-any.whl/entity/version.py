import time


class Version():
    def __init__(self):
        self.bump_version()

    def bump_version(self):
        localtime = time.localtime()
        timeString = time.strftime("%Y-%m-%d-%H%M%S", localtime)
        self.timestamp = timeString