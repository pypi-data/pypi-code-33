#
# README
#  - This class exists because I don't like deque's api
#


# ------- #
# Imports #
# ------- #

from collections import deque


# ---- #
# Main #
# ---- #


class Queue:
    def __init__(self, aList=[]):
        validateInput(aList)
        self._data = deque(aList)

    def __len__(self):
        return len(self._data)

    def add(self, element):
        self._data.append(element)
        return self

    def pop(self):
        return self._data.popleft()


# ------- #
# Helpers #
# ------- #


def validateInput(aList):
    if not isinstance(aList, list):
        raise TypeError("aList must be an instance of list")
