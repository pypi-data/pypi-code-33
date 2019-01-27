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
        try:
            call(self.cmd, shell=True)
        except Exception as e:
            print(e)


if __name__ == "__main__":
    clear()
