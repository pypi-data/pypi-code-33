from sys import platform
from subprocess import call


class clear():
    def __init__(self):
        if 'win' not in platform:
            self.cmd = 'clear'
        else:
            self.cmd = 'cls'
        self.__clear()

    def __clear(self):
        call(self.cmd, shell=True)


if __name__ == "__main__":
    clear()
