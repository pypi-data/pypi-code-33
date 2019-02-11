from time import time


class Printer:

    def __init__(self, queue):
        self.__curStdout, self.__lastOutSendTime = "", time()
        self.__queue = queue

    @property
    def currentStdOut(self):
        return self.__curStdout

    def write(self, text):
        self.__curStdout += text

        if time() > self.__lastOutSendTime + 0.01:
            self.__queue.put(self.__curStdout)
            self.__curStdout, self.__lastOutSendTime = "", time()
