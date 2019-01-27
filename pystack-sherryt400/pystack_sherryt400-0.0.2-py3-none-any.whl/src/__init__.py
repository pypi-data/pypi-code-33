from threading import Condition

from stack.src.exception.stack_exception import StackException


class Stack:

    def __init__(self, size=None):
        self.__size = size
        self.__list = []
        self.__condition = Condition()
        pass

    def push(self, item, block=True):
        """
        :param item:
        :param block:
        :return:
        """

        # check if blocking is not necessary
        if not block and len(self.__list) == self.__size:
            raise StackException('size limit reached')

        self.__condition.acquire()
        while block and self.__size is not None and len(self.__list) == self.__size:
            self.__condition.wait()
            pass
        self.__list.append(item)
        self.__condition.notify()
        self.__condition.release()
        pass

    def pop(self, block=True):
        """
        :param block:
        :return:
        """

        # check if blocking is not necessary
        if not block and len(self.__list) == 0:
            raise StackException('pop on empty stack')

        self.__condition.acquire()
        while block and len(self.__list) == 0:
            self.__condition.wait()
            pass
        item = self.__list.pop()
        self.__condition.notify()
        self.__condition.release()
        return item

    pass
