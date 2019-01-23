from time import time

class SimpleTimer(object):
    def __init__(self):
        self._start = None
        self._elaps = 0.0

    def start(self):
        self._start = time()

    def pause(self):
        if self._start == None:
            raise Exception("Timer shouldn't been paused befor started")
        self._elaps += (time() - self._start)
        self._start = None

    def read(self):
        # self.pause()
        return self._elaps
