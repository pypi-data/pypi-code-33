"""
第一次尝试
"""


class NZP(object):

    def __init__(self):
        self._info = "This niuzepeng object!"

    def __str__(self):
        return self._info

    @staticmethod
    def show():
        return "This is first create my package!"
