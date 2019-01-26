from threading import Condition


class Stack:

    def __init__(self, size=None):
        self.__size = size
        self.__list = []
        self.__condition = Condition()
        pass

    def push(self, item):
        self.__condition.acquire()
        while self.__size is not None and len(self.__list) == self.__size:
            self.__condition.wait()
            pass
        self.__list.append(item)
        self.__condition.notify()
        self.__condition.release()
        pass

    def pop(self):
        self.__condition.acquire()
        while len(self.__list) == 0:
            self.__condition.wait()
            pass
        item = self.__list.pop()
        self.__condition.notify()
        self.__condition.release()
        return item

    pass
